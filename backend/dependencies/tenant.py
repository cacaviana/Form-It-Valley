"""Resolucao de tenant a partir das claims do JWT da Petra Suite.

O token e emitido pela plataforma (suite-api.petrasuite.ai) via itvalleysecurity
com claims extras: tenant_id, is_master, products (list de slugs) e
permissions ({slug: [perms]}).

Regras:
- tenant_id ausente -> 401 (token de outra geracao / forjado sem contexto).
- Produto 'calenda' fora de products -> 403 ProductNotSubscribed
  (tenant master passa sempre).
- O tenant NUNCA vem do cliente: rotas autenticadas usam este contexto;
  rotas publicas resolvem o tenant pelo documento do flow.
"""
from dataclasses import dataclass, field
from fastapi import Depends, HTTPException
from itvalleysecurity.fastapi import require_access

PRODUCT_SLUG = "calenda"


@dataclass(frozen=True)
class TenantContext:
    tenant_id: str
    is_master: bool = False
    products: tuple = ()
    permissions: dict = field(default_factory=dict)
    email: str | None = None


async def get_tenant_context(auth: dict = Depends(require_access)) -> TenantContext:
    """Extrai o contexto de tenant das claims do JWT ja validado.

    Levanta 401 se o token nao carrega tenant_id e 403 se o tenant
    nao assina o produto 'calenda' (master sempre passa).
    """
    claims = auth.get("claims", {}) or {}
    tenant_id = claims.get("tenant_id")
    if not tenant_id or not isinstance(tenant_id, str):
        raise HTTPException(
            status_code=401,
            detail="Token sem tenant_id. Faca login pela Petra Suite.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    is_master = bool(claims.get("is_master", False))
    products = claims.get("products") or []
    if not isinstance(products, list):
        products = []

    if not is_master and PRODUCT_SLUG not in products:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "ProductNotSubscribed",
                "message": f"Tenant '{tenant_id}' nao assina o produto '{PRODUCT_SLUG}'.",
                "product": PRODUCT_SLUG,
            },
        )

    permissions = claims.get("permissions") or {}
    if not isinstance(permissions, dict):
        permissions = {}

    return TenantContext(
        tenant_id=tenant_id,
        is_master=is_master,
        products=tuple(products),
        permissions=permissions,
        email=auth.get("email"),
    )
