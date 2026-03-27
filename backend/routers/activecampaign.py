from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.activecampaign_service import ActiveCampaignService

router = APIRouter(prefix="/api/activecampaign", tags=["activecampaign"])

_service = ActiveCampaignService()


@router.get("/lists")
async def list_lists():
    """Lista todas as listas do ActiveCampaign."""
    lists = await _service.list_lists()
    return lists


class AddContactRequest(BaseModel):
    email: str
    first_name: str
    last_name: Optional[str] = ""
    phone: Optional[str] = ""
    list_id: str


@router.post("/contacts")
async def add_contact(request: AddContactRequest):
    """Cria/atualiza contato no AC e adiciona a uma lista."""
    result = await _service.add_contact_to_list(
        email=request.email,
        first_name=request.first_name,
        last_name=request.last_name or "",
        phone=request.phone or "",
        list_id=request.list_id,
    )
    if not result["success"]:
        raise HTTPException(status_code=502, detail=result.get("error", "ActiveCampaign error"))
    return result
