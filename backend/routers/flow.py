from fastapi import APIRouter, HTTPException
from dtos.flow.save_flow.request import SaveFlowRequest
from services.flow_service import FlowService

router = APIRouter(prefix="/api/flows", tags=["flows"])

_service = FlowService()


@router.get("")
async def list_flows():
    """Lista todos os flows."""
    return await _service.list_all()


@router.get("/{flow_id}")
async def get_flow(flow_id: str):
    """Busca flow por ID."""
    result = await _service.get_by_id(flow_id)
    if not result:
        raise HTTPException(status_code=404, detail="Flow nao encontrado")
    return result


@router.get("/slug/{slug}")
async def get_flow_by_slug(slug: str):
    """Busca flow por slug (URL publica)."""
    result = await _service.get_by_slug(slug)
    if not result:
        raise HTTPException(status_code=404, detail="Flow nao encontrado")
    return result


@router.post("", status_code=201)
async def create_flow(request: SaveFlowRequest):
    """Cria novo flow."""
    try:
        return await _service.create(request.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.put("/{flow_id}")
async def update_flow(flow_id: str, request: SaveFlowRequest):
    """Atualiza flow existente."""
    try:
        result = await _service.update(flow_id, request.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    if not result:
        raise HTTPException(status_code=404, detail="Flow nao encontrado")
    return result


@router.delete("/{flow_id}", status_code=204)
async def delete_flow(flow_id: str):
    """Remove flow."""
    deleted = await _service.delete(flow_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Flow nao encontrado")
