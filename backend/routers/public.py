from fastapi import APIRouter, HTTPException
from services.flow_service import FlowService
from services.submission_service import SubmissionService
from services.lead_service import LeadService
from services.gcal_service import GCalService
from services.notification_service import NotificationService
from services.activecampaign_service import ActiveCampaignService
from services.email_sender_service import EmailSenderService
from services.genesis_service import GenesisService
from services.sheets_service import SheetsService
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
_lead_service = LeadService()
_gcal = GCalService()
_notifications = NotificationService()
_activecampaign = ActiveCampaignService()
_sheets = SheetsService()
_genesis = GenesisService()
_email_sender = EmailSenderService()

logger = logging.getLogger(__name__)


@router.get("/flows/slug/{slug}")
async def get_flow_by_slug(slug: str):
    """Busca flow por slug (formulario publico — sem auth)."""
    result = await _flow_service.get_by_slug(slug)
    if not result:
        raise HTTPException(status_code=404, detail="Flow nao encontrado")
    return result


class CreateLeadRequest(BaseModel):
    flow_id: str
    flow_slug: str
    client_name: str
    client_email: str
    client_phone: Optional[str] = None
    client_phone_country_code: Optional[str] = None
    client_address: Optional[str] = None
    activecampaign_list_id: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None


@router.post("/leads", status_code=201)
async def create_lead(request: CreateLeadRequest):
    """Cria lead ao clicar em Comecar — salva no MongoDB + ActiveCampaign (sem auth).

    O tenant e resolvido pelo documento do flow — nunca vem do cliente.
    """
    try:
        result = await _lead_service.create(request.model_dump())
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Erro ao criar lead")
        raise HTTPException(status_code=500, detail=str(e))


class SheetEntryRequest(BaseModel):
    flow_id: str
    node_id: str
    name: str
    email: str
    phone: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_content: Optional[str] = None
    utm_term: Optional[str] = None


@router.post("/sheet-entry", status_code=201)
async def create_sheet_entry(request: SheetEntryRequest):
    """Envia o lead pra planilha configurada no no 'sheet' do flow (sem auth).

    A URL da planilha vem do flow salvo no MongoDB — nunca do cliente.
    """
    flow = await _flow_service.get_by_id(request.flow_id)
    if not flow:
        raise HTTPException(status_code=404, detail="Flow nao encontrado")

    node = next(
        (
            n for n in flow.get("nodes", [])
            if n.get("id") == request.node_id and n.get("type") == "sheet"
        ),
        None,
    )
    if not node:
        raise HTTPException(status_code=404, detail="No de planilha nao encontrado no flow")

    node_data = node.get("data", {})
    sheet_url = node_data.get("sheetUrl", "")
    if not sheet_url:
        raise HTTPException(status_code=422, detail="No de planilha sem URL configurada")

    result = await _sheets.append_lead(
        sheet_url=sheet_url,
        tab=node_data.get("sheetTab"),
        data={
            "name": request.name,
            "email": request.email,
            "phone": request.phone,
            "flow_slug": flow.get("slug", ""),
            "utm_source": request.utm_source,
            "utm_medium": request.utm_medium,
            "utm_campaign": request.utm_campaign,
            "utm_content": request.utm_content,
            "utm_term": request.utm_term,
        },
    )
    return result


class EmailNodeRequest(BaseModel):
    flow_id: str
    node_id: str
    name: str
    email: str
    phone: Optional[str] = None


@router.post("/email-node", status_code=201)
async def send_email_node(request: EmailNodeRequest):
    """Envia o e-mail configurado no no 'Enviar E-mail' do flow (sem auth).

    Assunto/corpo vem do flow salvo no MongoDB — nunca do cliente.
    """
    flow = await _flow_service.get_by_id(request.flow_id)
    if not flow:
        raise HTTPException(status_code=404, detail="Flow nao encontrado")

    node = next(
        (
            n for n in flow.get("nodes", [])
            if n.get("id") == request.node_id and n.get("type") == "email"
        ),
        None,
    )
    if not node:
        raise HTTPException(status_code=404, detail="No de e-mail nao encontrado no flow")

    node_data = node.get("data", {})
    subject = node_data.get("emailSubject", "")
    body = node_data.get("emailBody", "")
    if not subject and not body:
        raise HTTPException(status_code=422, detail="No de e-mail sem assunto/corpo configurado")

    result = await _email_sender.send_node_email(
        to_email=request.email,
        subject_template=subject,
        body_template=body,
        lead_values={
            "nome": request.name,
            "email": request.email,
            "telefone": request.phone or "",
            "formulario": flow.get("name", ""),
        },
    )
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
async def get_dates(month: int, year: int, flow_id: Optional[str] = None):
    """Retorna dias disponiveis (lead agendando — sem auth). flow_id usado para config personalizada."""
    return await _gcal.get_available_dates(month, year, flow_id)


@router.get("/scheduling/slots")
async def get_slots(date: str, flow_id: Optional[str] = None):
    """Retorna horarios disponiveis (lead agendando — sem auth). flow_id usado para config personalizada."""
    return await _gcal.get_available_slots(date, flow_id)


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


@router.post("/scheduling", status_code=201)
async def create_scheduling(request: PublicSchedulingRequest):
    """Cria agendamento (lead agendando — sem auth)."""
    try:
        # Le titulo customizado do evento (se houver) do flow
        event_title = None
        if request.flow_id:
            try:
                from data.repositories.mongo.flow_repository import FlowRepository
                flow_pre = await FlowRepository().find_by_id(request.flow_id)
                if flow_pre:
                    et = flow_pre.get("gcal_event_title")
                    if isinstance(et, str) and et.strip():
                        event_title = et.strip()
            except Exception:
                pass

        gcal_result = await _gcal.create_event(
            lead_name=request.lead_name,
            lead_email=request.lead_email,
            lead_phone=request.lead_phone or "",
            scheduled_date=request.scheduled_date,
            scheduled_time=request.scheduled_time,
            event_title=event_title,
            flow_id=request.flow_id,
        )
        meet_link = gcal_result.get("meet_link", "") if gcal_result else ""
        calendar_link = gcal_result.get("html_link", "") if gcal_result else ""

        # Override: se o flow tem meeting_link_override, usa esse link nas notificacoes
        email_cfg = None
        if request.flow_id:
            try:
                from data.repositories.mongo.flow_repository import FlowRepository
                flow_doc = await FlowRepository().find_by_id(request.flow_id)
                if flow_doc:
                    override = flow_doc.get("meeting_link_override")
                    if isinstance(override, str) and override.strip():
                        meet_link = override.strip()
                    ec = flow_doc.get("email_config")
                    if isinstance(ec, dict):
                        email_cfg = ec
            except Exception:
                pass

        gcal_event_id_local = gcal_result.get("event_id") if gcal_result else None
        email_task = _notifications.send_scheduling_email(
            lead_name=request.lead_name,
            lead_email=request.lead_email,
            scheduled_date=request.scheduled_date,
            scheduled_time=request.scheduled_time,
            calendar_link=calendar_link,
            meet_link=meet_link,
            email_config=email_cfg,
            event_title=event_title,
            event_id=gcal_event_id_local,
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

        # Tenant sai do documento do flow (rota publica — nunca do cliente)
        sched_tenant_id = None
        if request.flow_id:
            try:
                from data.repositories.mongo.flow_repository import FlowRepository
                _f = await FlowRepository().find_by_id(request.flow_id)
                if _f:
                    sched_tenant_id = _f.get("tenant_id")
            except Exception:
                pass
        if not sched_tenant_id and request.flow_slug:
            try:
                from data.repositories.mongo.flow_repository import FlowRepository
                _f = await FlowRepository().find_by_slug(request.flow_slug)
                if _f:
                    sched_tenant_id = _f.get("tenant_id")
            except Exception:
                pass

        db = mongodb_client.database
        doc = {
            "tenant_id": sched_tenant_id,
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
            "status": "confirmed",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        result = await db["scheduling"].insert_one(doc)
        doc.pop("_id", None)

        # Planilha: se o flow tem no 'sheet', preenche data/hora do agendamento
        if request.flow_id:
            try:
                flow_full = await _flow_service.get_by_id(request.flow_id)
                sheet_nodes = [
                    n for n in (flow_full or {}).get("nodes", [])
                    if n.get("type") == "sheet" and n.get("data", {}).get("sheetUrl")
                ]
                for sheet_node in sheet_nodes:
                    node_data = sheet_node.get("data", {})
                    await _sheets.update_scheduling(
                        sheet_url=node_data["sheetUrl"],
                        tab=node_data.get("sheetTab"),
                        email=request.lead_email,
                        scheduled_date=request.scheduled_date,
                        scheduled_time=request.scheduled_time,
                        fallback_data={
                            "name": request.lead_name,
                            "phone": request.lead_phone,
                            "flow_slug": request.flow_slug or (flow_full or {}).get("slug", ""),
                        },
                    )
            except Exception as e:
                logger.error(f"Erro ao atualizar planilha com agendamento: {e}")

        # Genesis CRM (Fase 1b): agendamento confirmado — nao-fatal
        try:
            await _genesis.send_lead(
                evento="agendamento_confirmado",
                nome=request.lead_name,
                email=request.lead_email,
                telefone=request.lead_phone or "",
                flow_slug=request.flow_slug or "",
                agendamento_data=request.scheduled_date,
                agendamento_hora=request.scheduled_time,
            )
        except Exception as e:
            logger.error(f"Erro ao enviar agendamento pro Genesis: {e}")

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
