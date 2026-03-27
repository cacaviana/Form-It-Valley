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
    ) -> bool:
        api_key = settings.resend_api_key
        if not api_key:
            logger.warning("RESEND_API_KEY nao configurada — e-mail nao enviado")
            return False

        from_email = settings.email_from or "onboarding@resend.dev"
        formatted_date = _format_date_pt_br(scheduled_date)

        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 20px;">
            <div style="background: #2563eb; color: white; padding: 20px; border-radius: 12px 12px 0 0; text-align: center;">
                <h2 style="margin: 0;">Agendamento Confirmado!</h2>
                <p style="margin: 8px 0 0; opacity: 0.85;">IT Valley - Escola de Tecnologia</p>
            </div>
            <div style="background: #f9fafb; padding: 24px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 12px 12px;">
                <p style="color: #374151; font-size: 15px;">Ola, <strong>{lead_name}</strong>!</p>
                <p style="color: #6b7280; font-size: 14px;">Seu atendimento foi agendado com sucesso.</p>
                <div style="background: white; border: 1px solid #d1d5db; border-radius: 8px; padding: 16px; margin: 16px 0;">
                    <p style="margin: 0 0 8px; color: #374151;"><strong>Data:</strong> {formatted_date}</p>
                    <p style="margin: 0; color: #374151;"><strong>Horario:</strong> {scheduled_time}</p>
                </div>
                {'<a href="' + calendar_link + '" style="display: block; background: #2563eb; color: white; text-align: center; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 14px;">Ver Evento no Google Calendar</a>' if calendar_link else ''}
                <p style="color: #9ca3af; font-size: 12px; margin-top: 16px; text-align: center;">
                    IT Valley School - Escola de Tecnologia
                </p>
            </div>
        </div>
        """

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
                        "subject": f"Agendamento confirmado - {formatted_date} as {scheduled_time}",
                        "html": html_body,
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
    """Normaliza telefone e detecta pais.

    Formatos aceitos:
      BR: "27995130691", "5527995130691", "+55 27 99513-0691"
      CA/US: "+1 (581) 578-0564", "15815780564", "5815780564"

    Retorna (telefone_com_codigo_pais, country_code_ISO).
    """
    digits = re.sub(r"\D", "", phone)

    # +55 ou 55 na frente → Brasil (13 digitos)
    if len(digits) == 13 and digits.startswith("55"):
        return digits, "BR"

    # +1 na frente → Canada/US (11 digitos: 1 + 10)
    if len(digits) == 11 and digits.startswith("1"):
        return digits, "CA"

    # 11 digitos sem prefixo internacional → Brasil (DDD + 9 + 8 digitos)
    if len(digits) == 11 and not digits.startswith("1"):
        return f"55{digits}", "BR"

    # 10 digitos → assume BR (DDD + 8 digitos, falta o 9)
    if len(digits) == 10:
        ddd = digits[:2]
        num = digits[2:]
        return f"55{ddd}9{num}", "BR"

    # 12 digitos: 55 + DDD + 8 digitos (BR sem o 9)
    if len(digits) == 12 and digits.startswith("55"):
        ddd = digits[2:4]
        num = digits[4:]
        return f"55{ddd}9{num}", "BR"

    # Fallback: tenta detectar pelo prefixo
    if digits.startswith("55") and len(digits) >= 12:
        return digits, "BR"
    if digits.startswith("1") and len(digits) >= 11:
        return digits, "CA"

    # Ultimo recurso: assume BR e adiciona 55
    if len(digits) >= 10:
        return f"55{digits}", "BR"

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
