from typing import Optional
from data.repositories.mongo.flow_repository import FlowRepository
from factories.flow_factory import FlowFactory
from mappers.flow_mapper import FlowMapper


class FlowService:
    """Camada opaca — orquestra Factory, Repository e Mapper.

    NAO conhece campos do flow. Delega tudo.
    Toda operacao autenticada e escopada por tenant_id (vindo do JWT).
    Lookups publicos (get_by_slug / get_by_id sem tenant) servem para
    resolver o tenant a partir do proprio documento do flow.
    """

    def __init__(self):
        self._repository = FlowRepository()
        self._factory = FlowFactory
        self._mapper = FlowMapper

    async def list_all(self, tenant_id: str) -> dict:
        docs = await self._repository.find_all(tenant_id=tenant_id)
        summaries = [self._mapper.to_summary(doc) for doc in docs]
        return {"flows": summaries, "total": len(summaries)}

    async def get_by_id(self, id: str, tenant_id: Optional[str] = None) -> Optional[dict]:
        doc = await self._repository.find_by_id(id, tenant_id=tenant_id)
        if not doc:
            return None
        return self._mapper.to_response(doc)

    async def get_by_slug(self, slug: str, tenant_id: Optional[str] = None) -> Optional[dict]:
        doc = await self._repository.find_by_slug(slug, tenant_id=tenant_id)
        if not doc:
            return None
        return self._mapper.to_response(doc)

    async def resolve_tenant_by_flow_id(self, flow_id: str) -> Optional[str]:
        """Rota publica: descobre a qual tenant o flow pertence (nunca vem do cliente)."""
        doc = await self._repository.find_by_id(flow_id)
        if not doc:
            return None
        return doc.get("tenant_id")

    async def create(self, data: dict, tenant_id: str) -> dict:
        data = {**data, "tenant_id": tenant_id}
        flow_doc = self._factory.create_new(data)

        # Garantir slug unico — se ja existe, adiciona sufixo numerico
        base_slug = flow_doc["slug"]
        existing = await self._repository.find_by_slug(base_slug)
        if existing:
            count = await self._repository.count_slugs_starting_with(base_slug)
            flow_doc["slug"] = f"{base_slug}-{count}"

        saved = await self._repository.insert(flow_doc)
        await self._subscribe_custom_calendar(saved)
        return self._mapper.to_response(saved)

    async def duplicate(self, id: str, new_name: str, tenant_id: str) -> Optional[dict]:
        """Duplica um flow existente com um novo nome.

        Copia todos os campos (nodes, edges, configs, etc.), regenera o slug
        a partir do novo nome (garantindo unicidade via create) e nasce como rascunho.
        """
        existing = await self._repository.find_by_id(id, tenant_id=tenant_id)
        if not existing:
            return None
        data = self._mapper.to_response(existing)
        # Remove identidade/versao do original — create() gera tudo novo
        for key in ("_id", "slug", "version", "created_at", "updated_at"):
            data.pop(key, None)
        data["name"] = new_name
        data["status"] = "draft"
        return await self.create(data, tenant_id)

    async def update(self, id: str, data: dict, tenant_id: str) -> Optional[dict]:
        existing = await self._repository.find_by_id(id, tenant_id=tenant_id)
        if not existing:
            return None
        update_data = self._factory.create_update(existing, data)
        updated = await self._repository.update(id, update_data, tenant_id=tenant_id)
        if not updated:
            return None
        await self._subscribe_custom_calendar(updated)
        return self._mapper.to_response(updated)

    async def _subscribe_custom_calendar(self, flow_doc: dict) -> None:
        """Se o flow tem gcal_calendar_id custom, garante que a agenda esta na lista da SA.

        Idempotente: chamar com a mesma agenda repetidas vezes nao causa problema.
        Falhas (ex: SA sem acesso) sao silenciosas — o flow continua sendo salvo.
        """
        cal_id = flow_doc.get("gcal_calendar_id")
        if not (isinstance(cal_id, str) and cal_id.strip()):
            return
        try:
            from services.gcal_service import GCalService
            await GCalService().subscribe_to_calendar(cal_id.strip())
        except Exception:
            pass

    async def delete(self, id: str, tenant_id: str) -> bool:
        return await self._repository.delete(id, tenant_id=tenant_id)
