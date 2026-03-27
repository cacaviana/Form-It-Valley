import asyncio
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

logger = logging.getLogger(__name__)
from services.gcal_service import GCalService
from services.notification_service import NotificationService
from services.activecampaign_service import ActiveCampaignService
from config.database import mongodb_client

router = APIRouter(prefix="/api/scheduling", tags=["scheduling"])

_gcal = GCalService()
_notifications = NotificationService()
_activecampaign = ActiveCampaignService()


@router.get("/dates")
async def get_dates(month: int, year: int):
    """Retorna dias do mes com disponibilidade."""
    return await _gcal.get_available_dates(month, year)


@router.get("/slots")
async def get_slots(date: str):
    """Retorna horarios disponiveis para uma data."""
    return await _gcal.get_available_slots(date)


class CreateSchedulingRequest(BaseModel):
    flow_id: Optional[str] = None
    flow_slug: Optional[str] = None
    lead_name: str
    lead_email: str
    lead_phone: Optional[str] = None
    lead_address: Optional[str] = None
    qualifying_answers: list[dict] = []
    scheduled_date: str
    scheduled_time: str
    whatsapp_template: Optional[str] = None
    whatsapp_variables: Optional[list[str]] = None
    activecampaign_list_id: Optional[str] = None


@router.post("", status_code=201)
async def create_scheduling(request: CreateSchedulingRequest):
    """Cria agendamento: Google Calendar + Email + WhatsApp + ActiveCampaign + MongoDB."""
    try:
        return await _do_create_scheduling(request)
    except Exception as e:
        logger.exception("Erro ao criar agendamento")
        raise HTTPException(status_code=500, detail=str(e))


async def _do_create_scheduling(request: CreateSchedulingRequest):
    # 1. Google Calendar
    gcal_result = await _gcal.create_event(
        lead_name=request.lead_name,
        lead_email=request.lead_email,
        lead_phone=request.lead_phone or "",
        scheduled_date=request.scheduled_date,
        scheduled_time=request.scheduled_time,
    )
    calendar_link = gcal_result["html_link"] if gcal_result else ""

    # 2. Email + WhatsApp em paralelo
    email_task = _notifications.send_scheduling_email(
        lead_name=request.lead_name,
        lead_email=request.lead_email,
        scheduled_date=request.scheduled_date,
        scheduled_time=request.scheduled_time,
        calendar_link=calendar_link,
    )

    if request.lead_phone:
        whatsapp_task = _notifications.send_whatsapp_notification(
            lead_name=request.lead_name,
            lead_phone=request.lead_phone,
            lead_email=request.lead_email,
            scheduled_date=request.scheduled_date,
            scheduled_time=request.scheduled_time,
            calendar_link=calendar_link,
            template_name=request.whatsapp_template,
            template_variables=request.whatsapp_variables,
        )
        email_sent, whatsapp_sent = await asyncio.gather(email_task, whatsapp_task)
    else:
        email_sent = await email_task
        whatsapp_sent = False

    # 3. ActiveCampaign
    ac_synced = False
    if request.activecampaign_list_id:
        name_parts = (request.lead_name or "").strip().split(" ")
        ac_result = await _activecampaign.add_contact_to_list(
            email=request.lead_email,
            first_name=name_parts[0] if name_parts else "",
            last_name=" ".join(name_parts[1:]) if len(name_parts) > 1 else "",
            phone=request.lead_phone or "",
            list_id=request.activecampaign_list_id,
        )
        ac_synced = ac_result.get("success", False)

    # 4. Salvar no MongoDB
    db = mongodb_client.database
    doc = {
        "flow_id": request.flow_id,
        "flow_slug": request.flow_slug,
        "lead_name": request.lead_name,
        "lead_email": request.lead_email,
        "lead_phone": request.lead_phone,
        "lead_address": request.lead_address,
        "qualifying_answers": request.qualifying_answers,
        "scheduled_date": request.scheduled_date,
        "scheduled_time": request.scheduled_time,
        "timezone": "America/Sao_Paulo",
        "duration_minutes": 30,
        "gcal_event_id": gcal_result["event_id"] if gcal_result else None,
        "gcal_event_link": calendar_link or None,
        "email_sent": email_sent,
        "whatsapp_sent": whatsapp_sent,
        "activecampaign_synced": ac_synced,
        "status": "confirmed",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    result = await db["scheduling"].insert_one(doc)

    # Remover _id do MongoDB (ObjectId nao e JSON-serializavel)
    doc.pop("_id", None)

    return {
        "id": str(result.inserted_id),
        **doc,
        "message": "Agendamento confirmado! Evento criado no Google Calendar."
        if gcal_result
        else "Agendamento confirmado! Voce recebera uma confirmacao em breve.",
    }
