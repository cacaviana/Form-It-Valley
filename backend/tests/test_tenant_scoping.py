"""Testes de escopo por tenant nos services — com fakes de Mongo (sem rede)."""
import pytest

from services.flow_service import FlowService
from services.lead_service import LeadService
from services.blacklist_service import BlacklistService


class FakeFlowRepository:
    """Fake do FlowRepository — grava as queries recebidas para inspecao."""

    def __init__(self, docs: list[dict]):
        self.docs = docs
        self.calls: list[tuple] = []

    async def find_all(self, tenant_id=None):
        self.calls.append(("find_all", tenant_id))
        return [d for d in self.docs if tenant_id is None or d.get("tenant_id") == tenant_id]

    async def find_by_id(self, id, tenant_id=None):
        self.calls.append(("find_by_id", id, tenant_id))
        for d in self.docs:
            if d["_id"] == id and (tenant_id is None or d.get("tenant_id") == tenant_id):
                return d
        return None

    async def find_by_slug(self, slug, tenant_id=None):
        for d in self.docs:
            if d["slug"] == slug and (tenant_id is None or d.get("tenant_id") == tenant_id):
                return d
        return None


FLOW_ITVALLEY = {
    "_id": "f1", "tenant_id": "itvalley", "name": "Flow A", "slug": "flow-a",
    "status": "published", "version": 1, "nodes": [], "edges": [],
    "created_at": "2026-01-01", "updated_at": "2026-01-01",
}
FLOW_OUTRO = {
    "_id": "f2", "tenant_id": "totalelectrique", "name": "Flow B", "slug": "flow-b",
    "status": "published", "version": 1, "nodes": [], "edges": [],
    "created_at": "2026-01-01", "updated_at": "2026-01-01",
}


@pytest.mark.asyncio
async def test_list_flows_filtra_por_tenant():
    service = FlowService()
    fake = FakeFlowRepository([FLOW_ITVALLEY, FLOW_OUTRO])
    service._repository = fake

    result = await service.list_all(tenant_id="itvalley")
    assert result["total"] == 1
    assert ("find_all", "itvalley") in fake.calls


@pytest.mark.asyncio
async def test_get_flow_de_outro_tenant_retorna_none():
    service = FlowService()
    service._repository = FakeFlowRepository([FLOW_OUTRO])

    result = await service.get_by_id("f2", tenant_id="itvalley")
    assert result is None


class FakeLeadRepository:
    def __init__(self):
        self.inserted = None

    async def find_by_email_and_flow(self, email, flow_slug, tenant_id=None):
        return None

    async def insert(self, document):
        self.inserted = {**document, "_id": "lead_1"}
        return self.inserted


@pytest.mark.asyncio
async def test_rota_publica_resolve_tenant_pelo_flow():
    """Lead publico: tenant NUNCA vem do cliente — sai do documento do flow."""
    service = LeadService()
    service._flow_repo = FakeFlowRepository([FLOW_ITVALLEY])
    fake_leads = FakeLeadRepository()
    service._repo = fake_leads
    # Integracoes externas nao devem rodar no teste
    service._ac = None
    service._genesis = type("G", (), {"send_lead": staticmethod(lambda **kw: _fail())})()

    data = {
        "flow_id": "f1",
        "flow_slug": "flow-a",
        "client_name": "Lead Teste",
        "client_email": "lead@x.com",
        # cliente tenta forjar outro tenant — deve ser ignorado
        "tenant_id": "hacker",
    }
    result = await service.create(data)
    assert fake_leads.inserted["tenant_id"] == "itvalley"
    assert result["tenant_id"] == "itvalley"


def _fail():
    raise RuntimeError("integracao externa nao deve rodar em teste")


@pytest.mark.asyncio
async def test_lead_publico_flow_inexistente_da_erro():
    service = LeadService()
    service._flow_repo = FakeFlowRepository([])
    with pytest.raises(ValueError):
        await service.create({
            "flow_id": "nao-existe", "flow_slug": "x",
            "client_name": "A", "client_email": "a@x.com",
        })


class FakeBlacklistRepository:
    def __init__(self, docs):
        self.docs = docs
        self.queries = []

    async def find_by_scope(self, scope_type, scope_id, tenant_id=None):
        self.queries.append((scope_type, scope_id, tenant_id))
        for d in self.docs:
            if d["scope_type"] == scope_type and d["scope_id"] == scope_id and (
                tenant_id is None or d.get("tenant_id") == tenant_id
            ):
                return d
        return None


class FakeAttemptsRepository:
    def __init__(self):
        self.inserted = []

    async def insert(self, doc):
        self.inserted.append(doc)
        return doc


@pytest.mark.asyncio
async def test_check_lead_publico_usa_tenant_do_flow():
    service = BlacklistService()
    service._flow_repo = FakeFlowRepository([FLOW_ITVALLEY])
    bl_repo = FakeBlacklistRepository([{
        "scope_type": "flow", "scope_id": "f1", "tenant_id": "itvalley",
        "entries": [{"email": "bloqueado@x.com", "phone": None}],
    }])
    service._repo = bl_repo
    attempts = FakeAttemptsRepository()
    service._attempts = attempts

    result = await service.check_lead(
        flow_id="f1", email="bloqueado@x.com", ddi=None, ddd=None, numero=None,
    )
    assert result["blocked"] is True
    assert result["matched_field"] == "email"
    # A query da blacklist foi escopada pelo tenant do flow
    assert ("flow", "f1", "itvalley") in bl_repo.queries
    # Auditoria gravada com o tenant do flow
    assert attempts.inserted[0]["tenant_id"] == "itvalley"


@pytest.mark.asyncio
async def test_check_lead_flow_inexistente_nao_bloqueia():
    service = BlacklistService()
    service._flow_repo = FakeFlowRepository([])
    service._repo = FakeBlacklistRepository([])
    service._attempts = FakeAttemptsRepository()

    result = await service.check_lead(
        flow_id="ghost", email="a@x.com", ddi=None, ddd=None, numero=None,
    )
    assert result["blocked"] is False
