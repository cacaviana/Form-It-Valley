"""Agente de orcamento com PydanticAI.

PROBLEMA CENTRAL
----------------
LLMs baratos (e às vezes os caros) cometem dois tipos de alucinação de catálogo:
  1. Substituição de nome  — "Camera 4K Ultra HD" vira "Camera IP 8MP" (produto similar presente no CSV)
  2. Substituição de preço — a IA mantém o nome correto mas usa o preço de um produto parecido

ARQUITETURA ANTI-ALUCINAÇÃO — 3 CAMADAS INDEPENDENTES
------------------------------------------------------
As camadas são projetadas para serem complementares: se uma falha (especialmente
em modelos baratos), as outras ainda protegem o resultado.

Camada 1 — PROMPT ESTRUTURADO  (build_context)
    Classifica cada resposta do cliente em três buckets ANTES de enviar à IA:

    • PRODUTOS CONFIRMADOS  — opção mapeada pelo admin (catalogProduct) OU match exato
      do value com o CSV. A IA recebe o nome e o preço correto e deve copiar sem alterar.

    • PRODUTOS AUSENTES     — opção com catalogProduct definido, mas o produto não está no
      CSV. A IA recebe instrução explícita: preço 0 + "(prix a consulter)", sem substituição.

    • OUTRAS RESPOSTAS      — contexto (região, amperagem, nome do cliente) ou seleções cujo
      nome não bate exatamente com o CSV. A IA decide se gera item, mas DEVE usar a descrição
      exata do cliente — INTERDIT de renomear para um produto do catálogo.

    Prompt usa seções com ## para compatibilidade com modelos menores.

Camada 2 — FUZZY MATCH RIGOROSO  (_find_catalog_match)
    Valida se uma string corresponde a algum produto do CSV.
    Ordem: exato → parcial → keyword.

    O keyword match exige:
      • ≥ 2 palavras "significativas" do produto do catálogo (len > 3 ou contém dígito)
      • Todas essas palavras presentes na descrição
    Isso impede que "Camera IP 4MP" bata com "Camera 4K Ultra HD" via
    a palavra genérica "camera" sozinha. Tokens com dígitos (4mp, 32a, 4k)
    são tratados como significativos mesmo tendo ≤ 3 caracteres.

Camada 3 — VALIDADOR PÓS-IA  (validate_quote)
    Código puro — não depende do comportamento do modelo.
    Para cada item que a IA retornou:

    a) Se encontra match no catálogo (via _find_catalog_match):
       • Força unit_price = preço do CSV (elimina alucinação de preço)
       • Se o item NÃO foi solicitado pelo cliente (AI adicionou por conta própria):
         força quantity = 1 (evita quantidades inventadas)

    b) Se NÃO encontra match no catálogo:
       • unit_price = 0, subtotal = 0
       • Adiciona sufixo "(prix a consulter)" se ausente

    c) CONFIRMADOS FORÇADOS — produtos que o sistema classificou como confirmados
       (catalog_map + exact matches) são re-verificados: se a IA os descreveu
       diferente e o validador não os encontrou, são injetados com o preço correto.
       Isso protege contra modelos over-conservative (ex: Haiku) que marcam tudo
       como "A consulter" mesmo quando o produto está confirmado no catálogo.

    Recalcula subtotais, TPS (5%) e TVQ (9,975%) sempre — independente do que a IA calculou.

DADOS DE TESTE
--------------
  Flow: devis-automacao-comercial  — 2 armadilhas (Camera 4K Ultra HD, Instalacao embutida teto)
  Flow: devis-dev-software         — 4 armadilhas (E-commerce avancado, App mobile hibrido,
                                      API GraphQL, SEO avancado)

RESULTADOS POR MODELO (2026-03-20)
-----------------------------------
  claude-sonnet-4  — 100% sem alucinação, itens confirmados precificados corretamente
  claude-haiku-4.5 — 0% substituição de nome/preço, mas over-conservative (marca tudo como
                     A consulter quando há muitos itens ausentes); Camada 3c corrige isso
  gpt-4o-mini      — Falha: substitui nomes e preços, ignora regras do prompt
"""

import csv
import io
import logging
import re
from dataclasses import dataclass

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

from config.settings import settings

logger = logging.getLogger(__name__)


# ── Output estruturado (o que o agente retorna) ──


class QuoteItem(BaseModel):
    """Um item do orcamento."""

    description: str = Field(description="Nom du produit ou service")
    unit_price: float = Field(description="Prix unitaire du catalogue CSV")
    quantity: int = Field(default=1, description="Quantite")
    subtotal: float = Field(description="unit_price * quantity")


class QuoteOutput(BaseModel):
    """Orcamento completo gerado pelo agente."""

    items: list[QuoteItem] = Field(description="Lignes du devis")
    subtotal: float = Field(description="Somme des items")
    taxes_tps: float = Field(description="TPS 5%")
    taxes_tvq: float = Field(description="TVQ 9.975%")
    total: float = Field(description="Total final TTC")
    recommendations: str = Field(
        description="Recommandations techniques basees sur les reponses"
    )
    notes: str = Field(
        default="",
        description="Notes additionnelles (subventions, conditions)",
    )


# ── Dependencias injetadas no agente ──


@dataclass
class QuoteDeps:
    pricing_csv: str  # CSV bruto do tenant
    answers: list[dict]  # Respostas do formulario
    business_rules: str  # businessContext do EndNode
    ai_instruction: str  # aiInstruction do EndNode
    client_name: str
    client_email: str
    client_phone: str
    client_address: str
    catalog_map: dict  # { answer_value_lower → catalogProduct } — mapeamento determinístico do admin


# ── Modelo da IA ──


def _setup_env():
    """Garante que as env vars estejam setadas para o PydanticAI."""
    import os
    if settings.openai_api_key and not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = settings.openai_api_key
    if settings.openai_base_url and not os.environ.get("OPENAI_BASE_URL"):
        os.environ["OPENAI_BASE_URL"] = settings.openai_base_url
    if settings.anthropic_api_key and not os.environ.get("ANTHROPIC_API_KEY"):
        os.environ["ANTHROPIC_API_KEY"] = settings.anthropic_api_key


_setup_env()


async def _get_model_name() -> str:
    """Busca modelo do DB (prioridade) ou cai no .env."""
    from routers.settings import get_ai_config
    try:
        cfg = await get_ai_config()
        provider = cfg["provider"]
        model = cfg["model"]
    except Exception:
        provider = settings.ai_provider.lower()
        model = settings.anthropic_model if provider == "anthropic" else settings.openai_model

    if provider == "anthropic" and settings.anthropic_api_key:
        return f"anthropic:{model}"
    if settings.openai_api_key:
        # Remove base_url residual do DeepSeek se estiver configurado
        import os
        os.environ.pop("OPENAI_BASE_URL", None)
        return f"openai:{model}"
    raise ValueError("Nenhuma API key configurada")


_AGENT_INSTRUCTIONS = """## Papel
Tu es un assistant de devis professionnel. Tu generes des devis STRICTEMENT bases sur les produits confirmes.

## REGRA PRINCIPAL
- Inclure UNIQUEMENT les produits listés dans "PRODUTOS SELECIONADOS PELO CLIENTE".
- INTERDIT d'ajouter des produits, subventions, rabais ou services supplementaires.
- INTERDIT d'inventer ou suggerer des produits que le client n'a pas choisi.
- Si aucun produit n'est selectionne: la liste d'items DOIT etre vide.

## Precos
- Utiliser UNIQUEMENT les prix indiques dans les produits confirmes. INTERDIT d'inventer un prix.
- Respecter la quantite exacte indiquee.

## Calcul
- TPS 5% + TVQ 9,975% sur le sous-total.
- Montants en dollars canadiens.

## Recommandations
- Utiliser les informations complementaires du client pour personnaliser les recommandations (texte libre).
- Les recommandations sont informatives SEULEMENT, jamais des items du devis."""

_agent_cache: dict[str, Agent] = {}


def _get_or_build_agent(model_name: str) -> Agent:
    if model_name in _agent_cache:
        return _agent_cache[model_name]
    agent = Agent(
        model=model_name,
        deps_type=QuoteDeps,
        output_type=QuoteOutput,
        instructions=_AGENT_INSTRUCTIONS,
    )
    agent.system_prompt(build_context)
    agent.output_validator(validate_quote)
    _agent_cache[model_name] = agent
    return agent


def build_context(ctx: RunContext[QuoteDeps]) -> str:
    """Injecte le contexte complet dans le prompt systeme."""
    csv_table = _format_csv_for_prompt(ctx.deps.pricing_csv)

    # Classifica cada resposta em: produto confirmado, produto ausente, ou contexto puro.
    # Prioridade 1: admin mapeou explicitamente via catalogProduct no builder.
    # Prioridade 2: auto-detecção por match exato do value com o CSV.
    # O que não se encaixa em nenhum dos dois → contexto puro (região, amperagem, etc.).
    catalog = _parse_csv_catalog(ctx.deps.pricing_csv)

    confirmed: list[str] = []   # produtos com preço confirmado
    absent: list[str] = []      # produtos mapeados mas ausentes do CSV
    context_answers: list[str] = []  # respostas que são contexto, não produto

    # Primeiro passo: coletar quantidades e adicionar produtos de quantidade como confirmados
    quantity_overrides: dict[str, int] = {}  # produto_lower → quantidade
    qty_products_added: set[str] = set()  # produtos já adicionados via quantidade
    for answer in ctx.deps.answers:
        node_id = answer.get("node_id", "")
        qty_product = ctx.deps.catalog_map.get(f"{node_id}:__qty__", "")
        if qty_product:
            try:
                qty = int(float(str(answer.get("value", "1"))))
            except (ValueError, TypeError):
                qty = 1
            quantity_overrides[qty_product.lower()] = qty
            qty_products_added.add(qty_product.lower())

    # Segundo passo: classificar cada resposta
    for answer in ctx.deps.answers:
        value = str(answer.get("value", "")).strip()
        label = str(answer.get("label", value)).strip()
        node_id = answer.get("node_id", "")
        question = answer.get("question", node_id or "?")

        # Perguntas de quantidade já foram processadas acima — pular
        if ctx.deps.catalog_map.get(f"{node_id}:__qty__", ""):
            continue

        # Perguntas text/date/photo — forçar como contexto, nunca item
        if ctx.deps.catalog_map.get(f"{node_id}:__context__", ""):
            context_answers.append(f"  - {question}: {label}")
            continue

        # Prioridade 1: admin mapeou esta opção explicitamente (chave = node_id:value)
        admin_product = ctx.deps.catalog_map.get(f"{node_id}:{value.lower()}", "")
        if admin_product == "__SKIP__":
            # Opção sem produto associado (ex: "não") — ignorar
            continue
        if admin_product:
            if catalog:
                match = _find_catalog_match(admin_product, catalog)
                if match:
                    qty = quantity_overrides.get(admin_product.lower(), 1)
                    qty_str = f" x{qty}" if qty > 1 else ""
                    total = match['price'] * qty
                    confirmed.append(f"  - {admin_product}{qty_str} @ ${match['price']}/un = ${total} (cliente respondeu \"{label}\")")
                else:
                    absent.append(f"  - \"{admin_product}\" ausente do CSV → preco 0 + \"(prix a consulter)\"")
            else:
                absent.append(f"  - \"{admin_product}\" (sem CSV carregado) → preco 0 + \"(prix a consulter)\"")
            continue

        # Prioridade 2: auto-detecção por match exato do label ou value com o CSV
        if catalog:
            exact = next(
                (p for p in catalog if p["name"] in (value.lower(), label.lower()) or p["name_original"] in (value, label)),
                None,
            )
            if exact:
                qty = quantity_overrides.get(exact["name"], 1)
                qty_str = f" x{qty}" if qty > 1 else ""
                total = exact['price'] * qty
                confirmed.append(f"  - {exact['name_original']}{qty_str} @ ${exact['price']}/un = ${total} (auto-detectado)")
                continue

        # Sem match → contexto puro (usa label legível, não o value técnico)
        context_answers.append(f"  - {question}: {label}")

    # Terceiro passo: adicionar produtos de quantidade que NÃO foram adicionados por single_choice
    # (ex: Cablage par pied no flow Borne — só tem pergunta de quantidade, sem single_choice)
    confirmed_products = {c.split(" @")[0].strip().lstrip("- ").split(" x")[0].lower() for c in confirmed}
    for product_lower, qty in quantity_overrides.items():
        if product_lower not in confirmed_products:
            match = _find_catalog_match(product_lower, catalog)
            if match:
                total = match["price"] * qty
                confirmed.append(f"  - {match['name_original']} x{qty} @ ${match['price']}/{match.get('unit','un')} = ${total} (quantidade informada pelo cliente)")
            else:
                absent.append(f"  - \"{product_lower}\" x{qty} ausente do CSV → preco 0 + \"(prix a consulter)\"")

    # Monta seções do prompt
    confirmed_section = ""
    if confirmed:
        confirmed_section = (
            "\n\nPRODUTOS SELECIONADOS PELO CLIENTE — confirmados no catalogo:\n"
            "(Copie SOMENTE estes itens NO DEVIS com o preco exato. NAO altere nome nem preco. "
            "NAO adicione outros produtos do catalogo que o cliente NAO selecionou.)\n"
            + "\n".join(confirmed)
        )
    else:
        confirmed_section = (
            "\n\nATENCAO: O cliente NAO selecionou nenhum produto. "
            "O devis deve ter ZERO itens (lista vazia). "
            "NAO inclua produtos do catalogo por conta propria."
        )

    absent_section = ""
    if absent:
        absent_section = (
            "\n\nPRODUTOS SELECIONADOS PELO CLIENTE — AUSENTES do catalogo:\n"
            "(Incluir no devis com preco 0 e sufixo '(prix a consulter)'. NAO substituir por produto similar.)\n"
            + "\n".join(absent)
        )

    other_section = ""
    if context_answers:
        other_section = (
            "\n\nINFORMACOES COMPLEMENTARES DO CLIENTE (somente contexto, NUNCA viram itens no devis):\n"
            "(Use APENAS para personalizar recomendacoes e notas. "
            "JAMAIS transforme estas informacoes em linhas de produto/servico no devis.)\n"
            + "\n".join(context_answers)
        )

    prompt = f"""CATALOGUE DE PRIX (source de verite ABSOLUE — unicos produtos e precos autorizados):
{csv_table}{confirmed_section}{absent_section}{other_section}

REGRAS:
1. Os PRODUTOS CONFIRMADOS acima DEVEM estar no devis com o preco exato — nao alterar
2. Preco de qualquer item DEVE ser do catalogo — JAMAIS inventar preco
3. Para produtos por unidade (ex: por pe), multiplicar preco x quantidade
4. Se servico nao tiver preco no catalogo: incluir com preco 0 + "(prix a consulter)"
5. Informacoes pessoais do cliente (nome, email, telefone) NUNCA sao itens do devis

CLIENT:
Nom: {ctx.deps.client_name}
Email: {ctx.deps.client_email}
Tel: {ctx.deps.client_phone or 'N/A'}
Adresse: {ctx.deps.client_address or 'N/A'}"""

    if ctx.deps.business_rules:
        prompt += f"""

REGLES METIER SPECIFIQUES:
{ctx.deps.business_rules}"""

    if ctx.deps.ai_instruction:
        prompt += f"""

INSTRUCTIONS DE FORMAT:
{ctx.deps.ai_instruction}"""

    return prompt


def _build_client_mentions(answers: list[dict], catalog_map: dict) -> set[str]:
    """Constrói conjunto de palavras-chave vindas das respostas do cliente.

    Inclui valores das respostas, produtos mapeados pelo admin e palavras
    significativas dos títulos das perguntas.
    Usado pelo validador para distinguir itens solicitados pelo cliente de
    itens adicionados por iniciativa da IA (esses ficam com quantity=1).
    """
    mentioned: set[str] = set()
    for answer in answers:
        value = str(answer.get("value", "")).strip()
        question = str(answer.get("question", "")).strip()
        # Admin-mapped option
        admin_product = catalog_map.get(value.lower(), "")
        if admin_product:
            mentioned.add(admin_product.lower())
        # Raw answer value
        mentioned.add(value.lower())
        # Significant words from the question label (e.g. "cabeamento" from
        # "Metragem de cabeamento" links to "Cabeamento por metro")
        for word in question.lower().split():
            if len(word) > 4:
                mentioned.add(word)
    return mentioned


def _build_confirmed_products(
    answers: list[dict], catalog_map: dict, catalog: list[dict]
) -> list[dict]:
    """Camada 3c: devolve lista de {name_original, price, answer_value} para cada produto
    que o sistema classificou como CONFIRMADO (admin-mapped ou exact-match no CSV).

    Usado pelo validador para garantir que itens confirmados apareçam no devis mesmo
    que a IA os tenha omitido ou marcado erroneamente como 'A consulter'.
    """
    confirmed = []
    for answer in answers:
        value = str(answer.get("value", "")).strip()

        # Prioridade 1: admin mapeou via catalogProduct
        admin_product = catalog_map.get(value.lower(), "")
        if admin_product:
            match = _find_catalog_match(admin_product, catalog)
            if match:
                confirmed.append({"name": match["name_original"], "price": match["price"], "value": value})
            continue

        # Prioridade 2: match exato do value com CSV
        exact = next(
            (p for p in catalog if p["name"] == value.lower() or p["name_original"] == value),
            None,
        )
        if exact:
            confirmed.append({"name": exact["name_original"], "price": exact["price"], "value": value})

    return confirmed


async def validate_quote(ctx: RunContext[QuoteDeps], output: QuoteOutput) -> QuoteOutput:
    """Valide que les items existent dans le CSV et que les calculs sont corrects.

    Aplica as três sub-etapas da Camada 3 (ver docstring do módulo):
      3a: força preço do CSV para itens encontrados
      3b: força quantity=1 para itens adicionados pela IA (não solicitados)
      3c: re-injeta itens confirmados omitidos ou marcados errado pelo modelo
    """
    catalog = _parse_csv_catalog(ctx.deps.pricing_csv)
    client_mentions = _build_client_mentions(ctx.deps.answers, ctx.deps.catalog_map)

    if catalog:
        validated_items = []
        for item in output.items:
            match = _find_catalog_match(item.description, catalog)
            if match:
                # 3a: força preço do CSV
                item.unit_price = match["price"]
                # 3b: se a IA adicionou por conta própria, limita qty=1
                desc_lower = item.description.lower()
                client_requested = any(
                    mention in desc_lower or desc_lower in mention
                    for mention in client_mentions
                    if mention
                )
                if not client_requested:
                    item.quantity = 1
                # 3b+: para produtos por unidade (pied, metro, etc.) com qty=1,
                # tenta extrair a quantidade total da descrição quando a IA a embutiu
                # ex: "Cablage (12 pieds + 15 pieds = 27 pieds total)" → qty=27
                elif item.quantity == 1 and match.get("unit", "unidade") != "unidade":
                    numbers = [int(n) for n in re.findall(r'\b(\d+)\b', item.description) if int(n) > 1]
                    if numbers:
                        item.quantity = max(numbers)
                        logger.info(f"Qty extraída da descrição: {item.description!r} → qty={item.quantity}")
                item.subtotal = round(match["price"] * item.quantity, 2)
                validated_items.append(item)
            else:
                logger.warning(
                    f"Item hors catalogue: {item.description} @ ${item.unit_price}"
                )
                # Sem match → preço 0 + sufixo
                item.unit_price = 0
                item.quantity = 1
                item.subtotal = 0
                if "prix" not in item.description.lower() or "consulter" not in item.description.lower():
                    item.description = f"{item.description} (prix a consulter)"
                validated_items.append(item)

        # 3c: re-injeta confirmados que a IA omitiu ou marcou errado
        confirmed_products = _build_confirmed_products(
            ctx.deps.answers, ctx.deps.catalog_map, catalog
        )
        present_names = {it.description.lower().split(" (prix")[0] for it in validated_items}
        for cp in confirmed_products:
            name_lower = cp["name"].lower()
            # Verifica se já está presente com preço correto
            already_priced = any(
                name_lower in it.description.lower() and it.unit_price > 0
                for it in validated_items
            )
            if not already_priced:
                # Descobre a quantidade: procura na resposta original
                qty = 1
                for answer in ctx.deps.answers:
                    if str(answer.get("value", "")).strip() == cp["value"]:
                        try:
                            qty = int(answer.get("quantity", 1))
                        except (ValueError, TypeError):
                            qty = 1
                        break
                injected = QuoteItem(
                    description=cp["name"],
                    unit_price=cp["price"],
                    quantity=qty,
                    subtotal=round(cp["price"] * qty, 2),
                )
                validated_items.append(injected)
                logger.info(f"Camada 3c: item confirmado re-injetado: {cp['name']} @ ${cp['price']}")

        output.items = validated_items

    # Recalculate subtotals
    for item in output.items:
        expected = round(item.unit_price * item.quantity, 2)
        if abs(item.subtotal - expected) > 0.01:
            item.subtotal = expected

    # Recalculate total
    subtotal = round(sum(i.subtotal for i in output.items), 2)
    output.subtotal = subtotal

    tps = round(subtotal * 0.05, 2)
    tvq = round(subtotal * 0.09975, 2)
    output.taxes_tps = tps
    output.taxes_tvq = tvq
    output.total = round(subtotal + tps + tvq, 2)

    return output


def _detect_csv_delimiter(csv_text: str) -> str:
    """Detecta se o separador do CSV e ; ou ,"""
    first_line = csv_text.strip().split('\n')[0]
    return ';' if ';' in first_line else ','


def _normalize_number(val: str) -> float:
    """Normaliza número em qualquer formato: 1099 | 1099.50 | 1099,50 | 1.099,50 | 1,099.50"""
    val = val.strip()
    if not val:
        return 0.0

    has_comma = ',' in val
    has_dot = '.' in val

    if has_comma and has_dot:
        last_comma = val.rfind(',')
        last_dot = val.rfind('.')
        if last_comma > last_dot:
            # 1.099,50 (BR/FR) → comma is decimal
            val = val.replace('.', '').replace(',', '.')
        else:
            # 1,099.50 (US) → dot is decimal
            val = val.replace(',', '')
    elif has_comma:
        # 1099,50 → comma is decimal
        val = val.replace(',', '.')

    return float(val)


def _parse_csv_catalog(csv_text: str) -> list[dict]:
    """Parse le CSV en liste de produits avec prix."""
    if not csv_text or not csv_text.strip():
        return []

    try:
        delimiter = _detect_csv_delimiter(csv_text)
        reader = csv.DictReader(io.StringIO(csv_text.strip()), delimiter=delimiter)
        catalog = []
        for row in reader:
            name = row.get("produto", "").strip()
            price_str = row.get("preco", "0").strip()
            try:
                price = _normalize_number(price_str)
            except ValueError:
                continue
            if name:
                unit = row.get("unidade", "unidade").strip().lower() or "unidade"
                catalog.append({"name": name.lower(), "name_original": name, "price": price, "unit": unit})
        return catalog
    except Exception:
        return []


def _find_catalog_match(item_description: str, catalog: list[dict]) -> dict | None:
    """Trouve le produit du catalogue qui correspond le mieux a la description.

    Utilise une correspondance flexible pour gerer les variations de noms
    que l'IA peut generer (ex: 'Borne 32A Level 2' vs 'Borne 32A').
    """
    desc_lower = item_description.lower()

    # Exact match
    for product in catalog:
        if product["name"] == desc_lower or product["name_original"].lower() == desc_lower:
            return product

    # Partial match: catalog name is fully contained in the description or vice-versa
    best_match = None
    best_len = 0
    for product in catalog:
        if product["name"] in desc_lower or desc_lower in product["name"]:
            if len(product["name"]) > best_len:
                best_match = product
                best_len = len(product["name"])

    # Keyword match: ALL meaningful words from the catalog must appear in the description.
    # This prevents "installation murale intérieure" from matching "installation murale extérieure"
    # because "extérieure" would be absent from the description.
    # Tokens are "meaningful" if they are long words (>3 chars) OR contain digits (model codes
    # like "4mp", "8mp", "4k", "32a" etc. that discriminate between products).
    # IMPORTANT: requires at least 2 meaningful words — a single generic word like "mobile"
    # or "camera" is not specific enough to confirm a match.
    if not best_match:
        # Clean description tokens (strip punctuation like parentheses, +, =)
        desc_words = {re.sub(r'[^\w]', '', w) for w in desc_lower.split()}
        desc_words.discard('')

        for product in catalog:
            prod_words = set(product["name"].split())
            meaningful_prod_words = {
                w for w in prod_words
                if len(w) > 3 or (len(w) >= 2 and any(c.isdigit() for c in w))
            }
            if len(meaningful_prod_words) < 2:
                continue
            # Every meaningful word of the catalog product must appear in the description.
            # Prefix match handles French plurals: "pied" matches "pieds", "metro" matches "metros".
            # Minimum prod_word length of 4 for prefix matching avoids false positives on short words.
            if all(
                any(dw == pw or (len(pw) >= 4 and dw.startswith(pw)) for dw in desc_words)
                for pw in meaningful_prod_words
            ):
                if not best_match or len(meaningful_prod_words) > best_len:
                    best_match = product
                    best_len = len(meaningful_prod_words)

    return best_match


def _format_csv_for_prompt(csv_text: str) -> str:
    """Formata o CSV como tabela legivel para o prompt."""
    if not csv_text.strip():
        return "(Aucun catalogue de prix fourni)"

    try:
        delimiter = _detect_csv_delimiter(csv_text)
        reader = csv.DictReader(io.StringIO(csv_text.strip()), delimiter=delimiter)
        lines = []
        for row in reader:
            produto = row.get("produto", "").strip()
            preco_raw = row.get("preco", "0").strip()
            try:
                preco = _normalize_number(preco_raw)
            except ValueError:
                preco = 0.0
            unidade = row.get("unidade", "").strip()
            categoria = row.get("categoria", "").strip()
            lines.append(f"| {produto} | ${preco:.2f} | {unidade} | {categoria} |")

        if not lines:
            return "(CSV vide ou format invalide)"

        header = "| Produit | Prix | Unite | Categorie |"
        separator = "|---------|------|-------|-----------|"
        return "\n".join([header, separator] + lines)

    except Exception as e:
        logger.warning(f"Erro ao parsear CSV: {e}")
        return csv_text  # fallback: envia o texto bruto


def _format_quote_text(output: QuoteOutput, client_name: str) -> str:
    """Formata o QuoteOutput como texto legivel para o cliente final."""
    lines = []
    lines.append("=" * 50)
    lines.append("       DEVIS ESTIMATIF")
    lines.append("       Total Electrique")
    lines.append("=" * 50)
    lines.append(f"\nClient: {client_name}\n")
    lines.append("-" * 50)

    for item in output.items:
        qty_str = f" x{item.quantity}" if item.quantity > 1 else ""
        lines.append(f"  {item.description}{qty_str}")
        lines.append(f"    ${item.subtotal:,.2f}")

    lines.append("-" * 50)
    lines.append(f"  Sous-total:     ${output.subtotal:,.2f}")
    lines.append(f"  TPS (5%):       ${output.taxes_tps:,.2f}")
    lines.append(f"  TVQ (9.975%):   ${output.taxes_tvq:,.2f}")
    lines.append(f"  TOTAL:          ${output.total:,.2f}")
    lines.append("-" * 50)

    if output.recommendations:
        lines.append(f"\nRecommandations:\n{output.recommendations}")

    if output.notes:
        lines.append(f"\nNotes:\n{output.notes}")

    lines.append("\n" + "=" * 50)
    lines.append("Validite: 30 jours")
    lines.append("Inspection pre-installation gratuite")
    lines.append("Garantie 2 ans main d'oeuvre")
    lines.append("Permis municipal inclus")
    lines.append("=" * 50)

    return "\n".join(lines)


def _build_deterministic_items(answers: list[dict], catalog_map: dict, pricing_csv: str) -> list[QuoteItem]:
    """Constrói lista de itens deterministicamente, sem IA.

    Usa catalogProduct das opções e quantityProduct dos nodes number.
    """
    catalog = _parse_csv_catalog(pricing_csv)
    quantity_overrides: dict[str, int] = {}
    items_map: dict[str, QuoteItem] = {}  # product_lower → QuoteItem

    # Primeiro: coletar quantidades
    for answer in answers:
        node_id = answer.get("node_id", "")
        qty_product = catalog_map.get(f"{node_id}:__qty__", "")
        if qty_product:
            try:
                quantity_overrides[qty_product.lower()] = int(float(str(answer.get("value", "1"))))
            except (ValueError, TypeError):
                quantity_overrides[qty_product.lower()] = 1

    # Segundo: coletar produtos das respostas
    for answer in answers:
        node_id = answer.get("node_id", "")
        value = str(answer.get("value", "")).strip()
        label = str(answer.get("label", value)).strip()

        if catalog_map.get(f"{node_id}:__qty__", ""):
            continue
        if catalog_map.get(f"{node_id}:__context__", ""):
            continue

        admin_product = catalog_map.get(f"{node_id}:{value.lower()}", "")
        if admin_product == "__SKIP__":
            continue

        product_name = ""
        if admin_product:
            product_name = admin_product
        else:
            # Auto-detect do CSV
            match = next(
                (p for p in catalog if p["name"] in (value.lower(), label.lower()) or p["name_original"] in (value, label)),
                None,
            )
            if match:
                product_name = match["name_original"]

        if not product_name:
            continue

        # Buscar no catálogo
        cat_match = _find_catalog_match(product_name, catalog)
        if cat_match and product_name.lower() not in items_map:
            qty = quantity_overrides.get(product_name.lower(), 1)
            items_map[product_name.lower()] = QuoteItem(
                description=cat_match["name_original"],
                unit_price=cat_match["price"],
                quantity=qty,
                subtotal=cat_match["price"] * qty,
            )

    # Terceiro: adicionar produtos de quantidade não associados a single_choice
    for product_lower, qty in quantity_overrides.items():
        if product_lower not in items_map:
            match = _find_catalog_match(product_lower, catalog)
            if match:
                items_map[product_lower] = QuoteItem(
                    description=match["name_original"],
                    unit_price=match["price"],
                    quantity=qty,
                    subtotal=match["price"] * qty,
                )

    return list(items_map.values())


def _build_quantity_overrides(answers: list[dict], catalog_map: dict) -> dict[str, int]:
    """Extrai quantity overrides das respostas de perguntas number/rating vinculadas a produtos."""
    overrides: dict[str, int] = {}
    for answer in answers:
        node_id = answer.get("node_id", "")
        qty_product = catalog_map.get(f"{node_id}:__qty__", "")
        if qty_product:
            try:
                overrides[qty_product.lower()] = int(float(str(answer.get("value", "1"))))
            except (ValueError, TypeError):
                overrides[qty_product.lower()] = 1
    return overrides


def _apply_quantity_overrides(output: QuoteOutput, overrides: dict[str, int], pricing_csv: str) -> QuoteOutput:
    """Aplica quantidades determinísticas nos itens do orçamento (não confia na IA pra isso)."""
    catalog = _parse_csv_catalog(pricing_csv)
    catalog_by_name = {p["name"]: p for p in catalog}

    new_items = []
    for item in output.items:
        name_lower = item.description.lower().strip()
        qty = overrides.get(name_lower, None)
        if qty is not None:
            cat_entry = catalog_by_name.get(name_lower)
            unit_price = cat_entry["price"] if cat_entry else item.unit_price
            new_items.append(QuoteItem(
                description=item.description,
                unit_price=unit_price,
                quantity=qty,
                subtotal=unit_price * qty,
            ))
        else:
            new_items.append(item)

    subtotal = sum(i.subtotal for i in new_items)
    tps = round(subtotal * 0.05, 2)
    tvq = round(subtotal * 0.09975, 2)
    total = round(subtotal + tps + tvq, 2)

    return QuoteOutput(
        items=new_items,
        subtotal=subtotal,
        taxes_tps=tps,
        taxes_tvq=tvq,
        total=total,
        recommendations=output.recommendations,
        notes=output.notes,
    )


class QuoteGenerator:
    """Interface publica — chamada pelo SubmissionService."""

    @staticmethod
    async def generate(
        business_context: str,
        client_data: dict,
        answers: list[dict],
        ai_instruction: str = "",
        pricing_csv: str = "",
        catalog_map: dict | None = None,
    ) -> dict:
        """Gera orcamento usando PydanticAI com output estruturado.

        Retorna dict com 'quote_text' (formatado) e 'quote_data' (estruturado).
        """

        deps = QuoteDeps(
            pricing_csv=pricing_csv,
            answers=answers,
            business_rules=business_context,
            ai_instruction=ai_instruction,
            client_name=client_data.get("client_name", ""),
            client_email=client_data.get("client_email", ""),
            client_phone=client_data.get("client_phone", ""),
            client_address=client_data.get("client_address", ""),
            catalog_map=catalog_map or {},
        )

        # ── Itens determinísticos (sem IA) ──
        det_items = _build_deterministic_items(answers, catalog_map or {}, pricing_csv)
        subtotal = sum(i.subtotal for i in det_items)
        tps = round(subtotal * 0.05, 2)
        tvq = round(subtotal * 0.09975, 2)
        total = round(subtotal + tps + tvq, 2)

        # ── IA só para recomendações ──
        recommendations = ""
        notes = ""
        try:
            model_name = await _get_model_name()
            agent = _get_or_build_agent(model_name)
            result = await agent.run(
                "Genere le devis complet base sur les reponses du client et le catalogue de prix.",
                deps=deps,
            )
            quote_output: QuoteOutput = result.output
            recommendations = quote_output.recommendations
            notes = quote_output.notes
        except Exception as e:
            logger.warning(f"IA indisponible pour recommandations: {e}")

        final_output = QuoteOutput(
            items=det_items,
            subtotal=subtotal,
            taxes_tps=tps,
            taxes_tvq=tvq,
            total=total,
            recommendations=recommendations,
            notes=notes,
        )

        logger.info(f"Devis genere: {len(det_items)} items, total=${total}")

        return {
            "quote_text": _format_quote_text(final_output, deps.client_name),
            "quote_data": {
                "items": [item.model_dump() for item in det_items],
                "subtotal": subtotal,
                "taxes_tps": tps,
                "taxes_tvq": tvq,
                "total": total,
                "recommendations": recommendations,
                "notes": notes,
            },
        }

    @staticmethod
    def _generate_basic(client_data: dict, answers: list[dict]) -> str:
        """Fallback sem IA — lista as respostas."""
        client_text = (
            f"Nom: {client_data.get('client_name', '')}\n"
            f"Email: {client_data.get('client_email', '')}\n"
            f"Tel: {client_data.get('client_phone', 'N/A')}\n"
            f"Adresse: {client_data.get('client_address', 'N/A')}"
        )
        answers_text = "\n".join(
            f"- {a.get('question', '?')}: {a.get('value', '')}" for a in answers
        )
        return (
            "=" * 50 + "\n"
            "       DEVIS ESTIMATIF\n"
            "       Total Electrique\n"
            + "=" * 50 + "\n"
            f"\n{client_text}\n\n"
            "Reponses:\n"
            f"{answers_text}\n\n"
            "NOTE: Devis genere sans IA (erreur de connexion).\n"
            "Un specialiste vous contactera pour le devis detaille.\n"
            + "=" * 50
        )
