from typing import Optional
from data.repositories.mongo.submission_repository import SubmissionRepository
from data.repositories.mongo.flow_repository import FlowRepository
from factories.submission_factory import SubmissionFactory
from mappers.submission_mapper import SubmissionMapper
from services.quote_generator import QuoteGenerator


class SubmissionService:
    """Camada opaca — orquestra Factory, Repository, Mapper e QuoteGenerator."""

    def __init__(self):
        self._repository = SubmissionRepository()
        self._flow_repository = FlowRepository()
        self._factory = SubmissionFactory
        self._mapper = SubmissionMapper
        self._quote_generator = QuoteGenerator

    async def list_all(self) -> dict:
        docs = await self._repository.find_all()
        summaries = [self._mapper.to_summary(doc) for doc in docs]
        return {"submissions": summaries, "total": len(summaries)}

    async def list_by_flow(self, flow_id: str) -> dict:
        docs = await self._repository.find_by_flow(flow_id)
        items = [self._mapper.to_response(doc) for doc in docs]
        return {"submissions": items, "total": len(items)}

    async def get_by_id(self, id: str) -> Optional[dict]:
        doc = await self._repository.find_by_id(id)
        if not doc:
            return None
        return self._mapper.to_response(doc)

    async def create(self, data: dict) -> dict:
        # Buscar flow para pegar o end_node com businessContext
        flow_doc = await self._flow_repository.find_by_id(data["flow_id"])
        if not flow_doc:
            raise ValueError("Flow nao encontrado")

        # Encontrar o end_node
        end_node = None
        for node in flow_doc.get("nodes", []):
            if node.get("id") == data["end_node_id"]:
                end_node = node
                break

        if not end_node:
            raise ValueError("No final nao encontrado no flow")

        # Pegar pricing_csv do flow
        pricing_csv = flow_doc.get("pricing_csv", "")

        # Montar mapa node_id → catalogProduct a partir dos nós do flow.
        # Quando o admin vincula uma opção a um produto do CSV no builder,
        # esse mapeamento é usado para match determinístico (sem depender da IA).
        catalog_map = _build_catalog_map(flow_doc.get("nodes", []))

        # Criar submission via Factory
        submission_doc = self._factory.create_new(data, end_node)

        # Se o end_type for quote, gerar orcamento
        if submission_doc["end_type"] == "quote":
            quote_result = await self._quote_generator.generate(
                business_context=submission_doc.get("business_context", ""),
                ai_instruction=submission_doc.get("ai_instruction", ""),
                client_data=data,
                answers=data["answers"],
                pricing_csv=pricing_csv,
                catalog_map=catalog_map,
            )
            submission_doc["quote_text"] = quote_result["quote_text"]
            submission_doc["quote_data"] = quote_result["quote_data"]
            submission_doc["status"] = "quoted"

        # Salvar
        saved = await self._repository.insert(submission_doc)
        return self._mapper.to_response(saved)

    async def delete(self, id: str) -> bool:
        return await self._repository.delete(id)


def _build_catalog_map(nodes: list) -> dict[str, str]:
    """Constrói mapa { node_id:answer_value → catalogProduct | __SKIP__ | __QTY__:product } a partir dos nós do flow.

    Usa node_id como prefixo da chave para evitar colisão quando opções de
    perguntas diferentes usam o mesmo value (ex: "opcao_1" em várias perguntas).

    Opções COM catalogProduct → mapeiam pro produto.
    Opções SEM catalogProduct (ex: "não") → marcadas como __SKIP__.
    Perguntas rating/number COM quantityProduct → marcadas como __QTY__:produto
    (o valor numérico da resposta será a quantidade desse produto).
    """
    catalog_map: dict[str, str] = {}
    for node in nodes:
        node_id = node.get("id", "")
        data = node.get("data", {})

        # Perguntas text/date/photo — sempre contexto, nunca item
        if data.get("questionType") in ("text", "date", "photo"):
            catalog_map[f"{node_id}:__context__"] = "__CONTEXT__"
            continue

        # Perguntas number SEM quantityProduct — são informativas (ex: distância, metragem)
        if data.get("questionType") == "number" and not data.get("quantityProduct", "").strip():
            catalog_map[f"{node_id}:__context__"] = "__CONTEXT__"
            continue

        # Perguntas rating/number com quantityProduct associado
        quantity_product = data.get("quantityProduct", "").strip()
        if quantity_product and data.get("questionType") in ("rating", "number"):
            catalog_map[f"{node_id}:__qty__"] = quantity_product
            continue

        # Perguntas yes_no — são de navegação/fluxo, respostas viram contexto
        if data.get("questionType") == "yes_no":
            catalog_map[f"{node_id}:__context__"] = "__CONTEXT__"
            continue

        options = data.get("options", [])
        # Se ALGUMA opção do node tem catalogProduct → modo explícito (sem catalog = __SKIP__)
        # Se NENHUMA opção tem catalogProduct → modo auto-detect (deixa IA + CSV resolverem)
        any_has_catalog = any(o.get("catalogProduct", "").strip() for o in options)
        for opt in options:
            catalog_product = opt.get("catalogProduct", "").strip()
            value = opt.get("value", "").strip()
            label = opt.get("label", "").strip()
            if catalog_product and value:
                catalog_map[f"{node_id}:{value.lower()}"] = catalog_product
                if label:
                    catalog_map[f"{node_id}:{label.lower()}"] = catalog_product
            elif any_has_catalog and value:
                # Modo explícito: opção sem produto → ignorar
                catalog_map[f"{node_id}:{value.lower()}"] = "__SKIP__"
                if label:
                    catalog_map[f"{node_id}:{label.lower()}"] = "__SKIP__"
            # Se nenhuma opção tem catalogProduct → não adiciona ao map
            # Cai no auto-detect do quote_generator (match por nome no CSV)
    return catalog_map
