from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from dtos.flow.save_flow.request import SaveFlowRequest
from services.flow_service import FlowService
from dependencies.tenant import TenantContext, get_tenant_context

router = APIRouter(prefix="/api/flows", tags=["flows"])

_service = FlowService()


class DuplicateFlowRequest(BaseModel):
    name: str


@router.get("")
async def list_flows(ctx: TenantContext = Depends(get_tenant_context)):
    """Lista todos os flows do tenant."""
    return await _service.list_all(tenant_id=ctx.tenant_id)


@router.get("/{flow_id}")
async def get_flow(flow_id: str, ctx: TenantContext = Depends(get_tenant_context)):
    """Busca flow por ID (escopado ao tenant)."""
    result = await _service.get_by_id(flow_id, tenant_id=ctx.tenant_id)
    if not result:
        raise HTTPException(status_code=404, detail="Flow nao encontrado")
    return result


@router.get("/slug/{slug}")
async def get_flow_by_slug(slug: str, ctx: TenantContext = Depends(get_tenant_context)):
    """Busca flow por slug (escopado ao tenant)."""
    result = await _service.get_by_slug(slug, tenant_id=ctx.tenant_id)
    if not result:
        raise HTTPException(status_code=404, detail="Flow nao encontrado")
    return result


@router.post("", status_code=201)
async def create_flow(request: SaveFlowRequest, ctx: TenantContext = Depends(get_tenant_context)):
    """Cria novo flow no tenant do usuario autenticado."""
    try:
        return await _service.create(request.model_dump(), tenant_id=ctx.tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/{flow_id}/duplicate", status_code=201)
async def duplicate_flow(
    flow_id: str,
    request: DuplicateFlowRequest,
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Duplica um flow existente com um novo nome."""
    name = (request.name or "").strip()
    if not name:
        raise HTTPException(status_code=422, detail="Nome do novo fluxo e obrigatorio")
    try:
        result = await _service.duplicate(flow_id, name, tenant_id=ctx.tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    if not result:
        raise HTTPException(status_code=404, detail="Flow nao encontrado")
    return result


@router.put("/{flow_id}")
async def update_flow(
    flow_id: str,
    request: SaveFlowRequest,
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Atualiza flow existente (escopado ao tenant)."""
    try:
        result = await _service.update(flow_id, request.model_dump(), tenant_id=ctx.tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    if not result:
        raise HTTPException(status_code=404, detail="Flow nao encontrado")
    return result


@router.delete("/{flow_id}", status_code=204)
async def delete_flow(flow_id: str, ctx: TenantContext = Depends(get_tenant_context)):
    """Remove flow (escopado ao tenant)."""
    deleted = await _service.delete(flow_id, tenant_id=ctx.tenant_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Flow nao encontrado")
