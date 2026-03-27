from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from services.notification_service import NotificationService

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

_service = NotificationService()


class SendEmailRequest(BaseModel):
    lead_name: str
    lead_email: str
    scheduled_date: str
    scheduled_time: str
    calendar_link: str = ""


class SendWhatsAppRequest(BaseModel):
    lead_name: str
    lead_phone: str
    lead_email: Optional[str] = ""
    scheduled_date: str
    scheduled_time: str
    calendar_link: str = ""
    template_name: Optional[str] = None
    template_variables: Optional[list[str]] = None


@router.post("/email")
async def send_email(request: SendEmailRequest):
    """Envia e-mail de confirmacao de agendamento via Resend."""
    sent = await _service.send_scheduling_email(
        lead_name=request.lead_name,
        lead_email=request.lead_email,
        scheduled_date=request.scheduled_date,
        scheduled_time=request.scheduled_time,
        calendar_link=request.calendar_link,
    )
    return {"sent": sent}


@router.post("/whatsapp")
async def send_whatsapp(request: SendWhatsAppRequest):
    """Envia mensagem WhatsApp via microsservico IT Valley."""
    sent = await _service.send_whatsapp_notification(
        lead_name=request.lead_name,
        lead_phone=request.lead_phone,
        lead_email=request.lead_email or "",
        scheduled_date=request.scheduled_date,
        scheduled_time=request.scheduled_time,
        calendar_link=request.calendar_link,
        template_name=request.template_name,
        template_variables=request.template_variables,
    )
    return {"sent": sent}
