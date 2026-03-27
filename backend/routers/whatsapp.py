from fastapi import APIRouter
from services.whatsapp_service import WhatsAppService

router = APIRouter(prefix="/api/whatsapp-templates", tags=["whatsapp"])

_service = WhatsAppService()


@router.get("")
async def list_templates():
    """Lista templates aprovados do WhatsApp Business (API direta Meta)."""
    return await _service.list_templates()
