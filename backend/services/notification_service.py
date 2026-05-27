import re
import httpx
import logging
from datetime import datetime
from typing import Optional
from config.settings import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """Envia notificacoes por Email (Resend) e WhatsApp (microsservico IT Valley)."""

    # ─── EMAIL (Resend) ───

    async def send_scheduling_email(
        self,
        lead_name: str,
        lead_email: str,
        scheduled_date: str,
        scheduled_time: str,
        calendar_link: str = "",
        meet_link: str = "",
        email_config: Optional[dict] = None,
        event_title: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> bool:
        api_key = settings.resend_api_key
        if not api_key:
            logger.warning("RESEND_API_KEY nao configurada — e-mail nao enviado")
            return False

        from_email_addr = settings.email_from or "onboarding@resend.dev"
        # Forca remetente exibido como "no-reply" (nao expoe nome real do remetente)
        from_email = f"no-reply <{from_email_addr}>"
        formatted_date = _format_date_pt_br(scheduled_date)

        # Defaults + override do email_config
        cfg = email_config or {}
        values = {
            "nome": lead_name,
            "data": formatted_date,
            "horario": scheduled_time,
            "link": meet_link or calendar_link or "",
            "email": lead_email,
        }
        subject = _resolve_placeholders(
            cfg.get("subject") or "Agendamento confirmado - {{data}} as {{horario}}",
            values
        )
        header_title = _resolve_placeholders(cfg.get("header_title") or "Agendamento Confirmado!", values)
        header_subtitle = _resolve_placeholders(cfg.get("header_subtitle") or "IT Valley - Escola de Tecnologia", values)
        greeting = _resolve_placeholders(cfg.get("greeting") or "Ola, <strong>{{nome}}</strong>!", values)
        body_text = _resolve_placeholders(cfg.get("body") or "Seu atendimento foi agendado com sucesso.", values)
        meet_button_text = cfg.get("meet_button_text") or "Entrar na Reuniao (Google Meet)"
        calendar_button_text = cfg.get("calendar_button_text") or "Ver Evento no Google Calendar"
        footer = _resolve_placeholders(cfg.get("footer") or "IT Valley School - Escola de Tecnologia", values)
        header_color = cfg.get("header_color") or "#2563eb"

        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 20px;">
            <div style="background: {header_color}; color: white; padding: 20px; border-radius: 12px 12px 0 0; text-align: center;">
                <h2 style="margin: 0;">{header_title}</h2>
                <p style="margin: 8px 0 0; opacity: 0.85;">{header_subtitle}</p>
            </div>
            <div style="background: #f9fafb; padding: 24px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 12px 12px;">
                <p style="color: #374151; font-size: 15px;">{greeting}</p>
                <p style="color: #6b7280; font-size: 14px;">{body_text}</p>
                <div style="background: white; border: 1px solid #d1d5db; border-radius: 8px; padding: 16px; margin: 16px 0;">
                    <p style="margin: 0 0 8px; color: #374151;"><strong>Data:</strong> {formatted_date}</p>
                    <p style="margin: 0; color: #374151;"><strong>Horario:</strong> {scheduled_time}</p>
                </div>
                {'<a href="' + meet_link + '" style="display: block; background: #00897b; color: white; text-align: center; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 14px;">' + meet_button_text + '</a>' if meet_link else ''}
                {'<a href="' + calendar_link + '" style="display: block; background: ' + header_color + '; color: white; text-align: center; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 14px; margin-top: 8px;">' + calendar_button_text + '</a>' if calendar_link else ''}
                <p style="color: #9ca3af; font-size: 12px; margin-top: 16px; text-align: center;">
                    {footer}
                </p>
            </div>
        </div>
        """

        # Gera ICS pra anexar — assim Gmail/Outlook adicionam o evento na agenda do lead automaticamente
        ics_content = _build_ics(
            title=event_title or header_title or "Agendamento",
            scheduled_date=scheduled_date,
            scheduled_time=scheduled_time,
            description=f"{body_text}\n\n{('Meet: ' + meet_link) if meet_link else ''}\n{('Calendar: ' + calendar_link) if calendar_link else ''}".strip(),
            location=meet_link or calendar_link or "",
            organizer_email=from_email_addr,
            attendee_email=lead_email,
            attendee_name=lead_name,
            uid=event_id,
        )
        import base64 as _b64
        ics_b64 = _b64.b64encode(ics_content.encode("utf-8")).decode("ascii")

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                res = await client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "from": from_email,
                        "to": [lead_email],
                        "subject": subject,
                        "html": html_body,
                        "attachments": [
                            {
                                "filename": "agendamento.ics",
                                "content": ics_b64,
                                "content_type": "text/calendar; charset=utf-8; method=REQUEST",
                            }
                        ],
                    },
                )

            if res.status_code == 200:
                result = res.json()
                logger.info(f"E-mail enviado para {lead_email} — id: {result.get('id')}")
                return True
            else:
                logger.error(f"Erro ao enviar e-mail: {res.text}")
                return False
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail: {e}")
            return False

    # ─── WHATSAPP (API direta Meta) ───

    async def send_whatsapp_notification(
        self,
        lead_name: str,
        lead_phone: str,
        scheduled_date: str,
        scheduled_time: str,
        calendar_link: str = "",
        lead_email: str = "",
        template_name: Optional[str] = None,
        template_variables: Optional[list[str]] = None,
    ) -> bool:
        from services.whatsapp_service import WhatsAppService
        wa = WhatsAppService()

        if not wa._configured():
            logger.warning("WhatsApp nao configurado — mensagem nao enviada")
            return False

        phone, _ = _normalize_phone(lead_phone)
        if not phone:
            logger.warning("Telefone invalido, WhatsApp nao enviado")
            return False

        template = template_name or settings.whatsapp_template_name or "teste0004"
        formatted_date = _format_date_pt_br(scheduled_date)

        # Resolve placeholders ou usa fallback padrao
        if template_variables and len(template_variables) > 0:
            variaveis = [
                _resolve_placeholders(v, {
                    "nome": lead_name,
                    "data": formatted_date,
                    "horario": scheduled_time,
                    "link": calendar_link or "Sera enviado por e-mail",
                    "email": lead_email,
                    "telefone": lead_phone,
                })
                for v in template_variables
            ]
        else:
            variaveis = [
                lead_name,
                f"Seu atendimento na IT Valley foi confirmado! Data: {formatted_date} - Horario: {scheduled_time}",
                f"Acesse o link da reuniao: {calendar_link}" if calendar_link else "Voce recebera o link da reuniao por e-mail. Ate la!",
            ]

        result = await wa.send_template_message(
            to_phone=phone,
            template_name=template,
            language="pt_BR",
            variables=variaveis,
        )
        return result.get("success", False)


# ─── Helpers ───

def _normalize_phone(phone: str) -> tuple[str, str]:
    """Normaliza telefone para formato E.164 (somente digitos com DDI).

    Aceita:
      - Formato novo (com DDI): "+55 27 99513-0691", "+33 6 12 34 56 78", "+1 (581) 578-0564"
      - Formato legado BR: "27995130691", "5527995130691"

    Retorna (telefone_somente_digitos_com_ddi, country_code_ISO).
    """
    digits = re.sub(r"\D", "", phone)

    if not digits or len(digits) < 7:
        return "", ""

    # DDIs conhecidos (ordenados do mais longo pro mais curto para match correto)
    _KNOWN_DDI = [
        ("972", "IL"), ("971", "AE"), ("598", "UY"), ("595", "PY"),
        ("351", "PT"),
        ("91", "IN"), ("86", "CN"), ("81", "JP"), ("61", "AU"),
        ("57", "CO"), ("56", "CL"), ("55", "BR"), ("54", "AR"),
        ("52", "MX"), ("49", "DE"), ("44", "GB"), ("41", "CH"),
        ("39", "IT"), ("34", "ES"), ("33", "FR"), ("32", "BE"),
        ("31", "NL"), ("27", "ZA"),
        ("7", "RU"),
        ("1", "US"),
    ]

    # Tenta detectar DDI no inicio dos digitos
    for ddi, country in _KNOWN_DDI:
        if digits.startswith(ddi):
            local = digits[len(ddi):]
            # Verifica se o numero local tem tamanho razoavel (>= 6 digitos)
            if len(local) >= 6:
                return digits, country

    # Fallback legado: 11 digitos sem DDI reconhecido → assume Brasil
    if len(digits) == 11:
        return f"55{digits}", "BR"

    # 10 digitos → assume BR (DDD + 8 digitos, falta o 9 do celular)
    if len(digits) == 10:
        ddd = digits[:2]
        num = digits[2:]
        return f"55{ddd}9{num}", "BR"

    return "", ""


def _resolve_placeholders(template: str, values: dict[str, str]) -> str:
    """Substitui placeholders {{nome}}, {{data}}, etc. pelo valor real."""
    def replacer(match: re.Match) -> str:
        key = match.group(1)
        return values.get(key, match.group(0))
    return re.sub(r"\{\{(\w+)\}\}", replacer, template)


def _format_date_pt_br(date_str: str) -> str:
    """Formata data YYYY-MM-DD para formato brasileiro legivel."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        weekdays = ["segunda-feira", "terca-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sabado", "domingo"]
        months = ["janeiro", "fevereiro", "marco", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
        weekday = weekdays[dt.weekday()]
        month = months[dt.month - 1]
        return f"{weekday}, {dt.day} de {month} de {dt.year}"
    except Exception:
        return date_str


def _ics_escape(text: str) -> str:
    """Escapa caracteres especiais no ICS conforme RFC 5545."""
    return (text or "").replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")


def _build_ics(
    title: str,
    scheduled_date: str,
    scheduled_time: str,
    description: str,
    location: str,
    organizer_email: str,
    attendee_email: str,
    attendee_name: str,
    uid: Optional[str] = None,
    duration_minutes: int = 30,
) -> str:
    """Gera arquivo ICS (RFC 5545) pra anexar no email — funciona em Gmail/Outlook/Apple Calendar.

    O lead recebe o email e o cliente de email reconhece o anexo, oferecendo botao
    "Adicionar a agenda" ou exibindo o evento inline.
    """
    import uuid as _uuid
    from datetime import timedelta

    if not uid:
        uid = f"{_uuid.uuid4()}@formitvalley"

    # Parse data/hora local (America/Sao_Paulo)
    try:
        start_local = datetime.strptime(f"{scheduled_date} {scheduled_time}", "%Y-%m-%d %H:%M")
    except Exception:
        start_local = datetime.now()
    end_local = start_local + timedelta(minutes=duration_minutes)

    # Formato sem TZ — usaremos TZID nos campos pra Sao Paulo
    def fmt_local(dt: datetime) -> str:
        return dt.strftime("%Y%m%dT%H%M%S")

    # DTSTAMP em UTC
    dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//FormItValley//Scheduling//PT-BR",
        "METHOD:REQUEST",
        "CALSCALE:GREGORIAN",
        "BEGIN:VTIMEZONE",
        "TZID:America/Sao_Paulo",
        "BEGIN:STANDARD",
        "DTSTART:19700101T000000",
        "TZOFFSETFROM:-0300",
        "TZOFFSETTO:-0300",
        "TZNAME:BRT",
        "END:STANDARD",
        "END:VTIMEZONE",
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{dtstamp}",
        f"DTSTART;TZID=America/Sao_Paulo:{fmt_local(start_local)}",
        f"DTEND;TZID=America/Sao_Paulo:{fmt_local(end_local)}",
        f"SUMMARY:{_ics_escape(title)}",
        f"DESCRIPTION:{_ics_escape(description)}",
        f"LOCATION:{_ics_escape(location)}",
        f"ORGANIZER;CN={_ics_escape('No Reply')}:mailto:{organizer_email}",
        f"ATTENDEE;CN={_ics_escape(attendee_name)};ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=TRUE:mailto:{attendee_email}",
        "STATUS:CONFIRMED",
        "TRANSP:OPAQUE",
        "SEQUENCE:0",
        "END:VEVENT",
        "END:VCALENDAR",
    ]
    # CRLF é exigido pelo padrao
    return "\r\n".join(lines)
