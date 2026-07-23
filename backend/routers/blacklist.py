from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from dtos.blacklist.upload_csv.response import UploadBlacklistCsvResponse
from dtos.blacklist.check_lead.request import CheckLeadRequest
from dtos.blacklist.check_lead.response import CheckLeadResponse
from services.blacklist_service import BlacklistService
from dependencies.tenant import TenantContext, get_tenant_context


class AddEntryRequest(BaseModel):
    email: Optional[str] = None
    ddi: Optional[str] = None
    ddd: Optional[str] = None
    numero: Optional[str] = None


class RemoveEntryRequest(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None  # ja normalizado (so digitos)

router = APIRouter(prefix="/api/blacklist", tags=["blacklist"])
public_router = APIRouter(prefix="/api/public/blacklist", tags=["blacklist-public"])

_service = BlacklistService()


@router.post("/upload", response_model=UploadBlacklistCsvResponse)
async def upload_csv(
    file: UploadFile = File(..., description="CSV com header email,ddi,ddd,numero"),
    scope_type: str = Form(default="flow"),
    scope_id: str = Form(...),
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Upload de CSV. Header obrigatorio: email,ddi,ddd,numero."""
    raw = await file.read()
    try:
        csv_text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            csv_text = raw.decode("latin-1")
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="Encoding nao suportado (use UTF-8 ou Latin-1)")

    result = await _service.upload(
        csv_text=csv_text,
        scope_type=scope_type,
        scope_id=scope_id,
        tenant_id=ctx.tenant_id,
    )
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail={
            "message": "CSV invalido",
            "errors": result.get("errors", []),
        })
    return UploadBlacklistCsvResponse(
        blacklist_id=result["blacklist_id"],
        total_entries=result["total_entries"],
        skipped_lines=result["skipped_lines"],
        errors=result["errors"],
        csv_uploaded_at=result["csv_uploaded_at"],
    )


@router.get("/by-flow/{flow_id}")
async def get_metadata(flow_id: str, ctx: TenantContext = Depends(get_tenant_context)):
    """Metadados (total, last_upload). NAO devolve as entries por privacidade."""
    meta = await _service.get_metadata("flow", flow_id, tenant_id=ctx.tenant_id)
    if not meta:
        return {"exists": False, "total_entries": 0}
    return {"exists": True, **meta}


@router.delete("/by-flow/{flow_id}", status_code=204)
async def delete_blacklist(flow_id: str, ctx: TenantContext = Depends(get_tenant_context)):
    deleted = await _service.delete("flow", flow_id, tenant_id=ctx.tenant_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Blacklist nao encontrada")
    return None


@router.get("/by-flow/{flow_id}/attempts")
async def list_attempts(flow_id: str, ctx: TenantContext = Depends(get_tenant_context)):
    """Historico de tentativas bloqueadas para o flow."""
    attempts = await _service.list_attempts(flow_id, tenant_id=ctx.tenant_id)
    return {"attempts": attempts, "total": len(attempts)}


@router.get("/by-flow/{flow_id}/entries")
async def list_entries(flow_id: str, ctx: TenantContext = Depends(get_tenant_context)):
    """Lista completa das entries da blacklist. APENAS admin autenticado."""
    entries = await _service.list_entries("flow", flow_id, tenant_id=ctx.tenant_id)
    return {"entries": entries, "total": len(entries)}


@router.post("/by-flow/{flow_id}/entries", status_code=201)
async def add_entry(
    flow_id: str,
    payload: AddEntryRequest,
    ctx: TenantContext = Depends(get_tenant_context),
):
    result = await _service.add_entry(
        tenant_id=ctx.tenant_id,
        scope_type="flow",
        scope_id=flow_id,
        email=payload.email,
        ddi=payload.ddi,
        ddd=payload.ddd,
        numero=payload.numero,
    )
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("error", "Erro"))
    return {"ok": True, "total_entries": result["total_entries"]}


@router.delete("/by-flow/{flow_id}/entries")
async def remove_entry(
    flow_id: str,
    payload: RemoveEntryRequest,
    ctx: TenantContext = Depends(get_tenant_context),
):
    result = await _service.remove_entry(
        scope_type="flow",
        scope_id=flow_id,
        email=payload.email,
        phone=payload.phone,
        tenant_id=ctx.tenant_id,
    )
    if not result.get("ok"):
        raise HTTPException(status_code=404, detail=result.get("error", "Entrada nao encontrada"))
    return {"ok": True, "total_entries": result["total_entries"]}


@public_router.post("/check", response_model=CheckLeadResponse)
async def check_lead(payload: CheckLeadRequest):
    """Endpoint publico — frontend chama antes do agendamento.

    Sem auth (lead anonimo). O tenant e resolvido pelo documento do flow —
    NUNCA vem do cliente. Retorna {blocked, matched_field}.
    """
    result = await _service.check_lead(
        flow_id=payload.flow_id,
        email=payload.email,
        ddi=payload.ddi,
        ddd=payload.ddd,
        numero=payload.numero,
    )
    return CheckLeadResponse(blocked=result["blocked"], matched_field=result.get("matched_field"))
