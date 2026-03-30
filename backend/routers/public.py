from fastapi import APIRouter, HTTPException
from services.flow_service import FlowService
from services.submission_service import SubmissionService
from services.gcal_service import GCalService
from services.notification_service import NotificationService
from services.activecampaign_service import ActiveCampaignService
from dtos.submission.create_submission.request import CreateSubmissionRequest
from dtos.submission.create_submission.response import CreateSubmissionResponse
from config.database import mongodb_client
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import asyncio
import logging

router = APIRouter(prefix="/api/public", tags=["public"])

_flow_service = FlowService()
_submission_service = SubmissionService()
_gcal = GCalService()
_notifications = NotificationService()
_activecampaign = ActiveCampaignService()

logger = logging.getLogger(__name__)


@router.get("/flows/slug/{slug}")
async def get_flow_by_slug(slug: str):
    """Busca flow por slug (formulario publico — sem auth)."""
    result = await _flow_service.get_by_slug(slug)
    if not result:
        raise HTTPException(status_code=404, detail="Flow nao encontrado")
    return result


@router.post("/submissions", status_code=201, response_model=CreateSubmissionResponse)
async def create_submission(request: CreateSubmissionRequest):
    """Cria submission (lead enviando formulario — sem auth)."""
    try:
        result = await _submission_service.create(request.model_dump())
        return CreateSubmissionResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/scheduling/dates")
async def get_dates(month: int, year: int):
    """Retorna dias disponiveis (lead agendando — sem auth)."""
    return await _gcal.get_available_dates(month, year)


@router.get("/scheduling/slots")
async def get_slots(date: str):
    """Retorna horarios disponiveis (lead agendando — sem auth)."""
    return await _gcal.get_available_slots(date)


class PublicSchedulingRequest(BaseModel):
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


@router.post("/scheduling", status_code=201)
async def create_scheduling(request: PublicSchedulingRequest):
    """Cria agendamento (lead agendando — sem auth)."""
    try:
        gcal_result = await _gcal.create_event(
            lead_name=request.lead_name,
            lead_email=request.lead_email,
            lead_phone=request.lead_phone or "",
            scheduled_date=request.scheduled_date,
            scheduled_time=request.scheduled_time,
        )
        meet_link = gcal_result.get("meet_link", "") if gcal_result else ""
        calendar_link = gcal_result.get("html_link", "") if gcal_result else ""

        email_task = _notifications.send_scheduling_email(
            lead_name=request.lead_name,
            lead_email=request.lead_email,
            scheduled_date=request.scheduled_date,
            scheduled_time=request.scheduled_time,
            calendar_link=calendar_link,
            meet_link=meet_link,
        )

        if request.lead_phone:
            whatsapp_task = _notifications.send_whatsapp_notification(
                lead_name=request.lead_name,
                lead_phone=request.lead_phone,
                lead_email=request.lead_email,
                scheduled_date=request.scheduled_date,
                scheduled_time=request.scheduled_time,
                calendar_link=meet_link or calendar_link,
                template_name=request.whatsapp_template,
                template_variables=request.whatsapp_variables,
            )
            email_sent, whatsapp_sent = await asyncio.gather(email_task, whatsapp_task)
        else:
            email_sent = await email_task
            whatsapp_sent = False

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
            "gcal_event_link": meet_link or calendar_link or None,
            "email_sent": email_sent,
            "whatsapp_sent": whatsapp_sent,
            "activecampaign_synced": ac_synced,
            "status": "confirmed",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        result = await db["scheduling"].insert_one(doc)
        doc.pop("_id", None)

        return {
            "id": str(result.inserted_id),
            **doc,
            "message": "Agendamento confirmado! Evento criado no Google Calendar."
            if gcal_result
            else "Agendamento confirmado! Voce recebera uma confirmacao em breve.",
        }
    except Exception as e:
        logger.exception("Erro ao criar agendamento publico")
        raise HTTPException(status_code=500, detail=str(e))
