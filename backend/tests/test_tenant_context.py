"""Testes da resolucao de tenant a partir das claims do JWT."""
import pytest
from fastapi import HTTPException

from dependencies.tenant import get_tenant_context, TenantContext, PRODUCT_SLUG


def _auth(claims: dict, email: str = "user@x.com") -> dict:
    """Simula o retorno de itvalleysecurity require_access."""
    return {"sub": email, "email": email, "claims": claims}


@pytest.mark.asyncio
async def test_resolve_tenant_das_claims():
    ctx = await get_tenant_context(_auth({
        "tenant_id": "itvalley",
        "is_master": False,
        "products": ["genesis", "calenda"],
        "permissions": {"calenda": ["calenda.view", "calenda.admin"]},
    }))
    assert isinstance(ctx, TenantContext)
    assert ctx.tenant_id == "itvalley"
    assert ctx.is_master is False
    assert "calenda" in ctx.products
    assert ctx.permissions["calenda"] == ["calenda.view", "calenda.admin"]
    assert ctx.email == "user@x.com"


@pytest.mark.asyncio
async def test_401_sem_tenant_id():
    with pytest.raises(HTTPException) as exc:
        await get_tenant_context(_auth({"products": ["calenda"]}))
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_403_sem_produto_calenda():
    with pytest.raises(HTTPException) as exc:
        await get_tenant_context(_auth({
            "tenant_id": "totalelectrique",
            "is_master": False,
            "products": ["genesis"],
        }))
    assert exc.value.status_code == 403
    assert exc.value.detail["error"] == "ProductNotSubscribed"
    assert exc.value.detail["product"] == PRODUCT_SLUG


@pytest.mark.asyncio
async def test_master_passa_sem_produto():
    ctx = await get_tenant_context(_auth({
        "tenant_id": "petra",
        "is_master": True,
        "products": [],
    }))
    assert ctx.tenant_id == "petra"
    assert ctx.is_master is True
