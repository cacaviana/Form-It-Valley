import logging
import re
from typing import Optional

import httpx

from config.settings import settings

logger = logging.getLogger(__name__)

_PLACEHOLDER_RE = re.compile(r"\{\{(\w+)\}\}")


def _resolve(template: str, values: dict) -> str:
    """Substitui {{chave}} pelos valores do lead (chaves desconhecidas viram '')."""
    return _PLACEHOLDER_RE.sub(lambda m: str(values.get(m.group(1), "")), template or "")


class EmailSenderService:
    """Envia e-mail do no 'Enviar E-mail' do flow builder (substitui autoresponder do AC).

    Providers:
    - ACS (Azure Communication Services): usado se ACS_EMAIL_CONNECTION_STRING +
      ACS_EMAIL_SENDER estiverem configurados (mesmo padrao do Petra-Genesis).
    - Resend: fallback — ja e o provider dos e-mails de agendamento em producao.
    Fire-and-forget: NUNCA levanta exception.
    """

    def _build_html(self, body_text: str) -> str:
        """Corpo simples e limpo — paragrafos separados por linha em branco."""
        paragraphs = "".join(
            f'<p style="color: #374151; font-size: 15px; line-height: 1.6; margin: 0 0 14px;">{p.strip()}</p>'
            for p in (body_text or "").split("\n\n")
            if p.strip()
        )
        return f"""
        <div style="font-family: Arial, sans-serif; max-width: 520px; margin: 0 auto; padding: 24px;">
            {paragraphs}
            <p style="color: #9ca3af; font-size: 12px; margin-top: 24px;">IT Valley School - Escola de Tecnologia</p>
        </div>
        """

    async def _send_acs(self, to_email: str, subject: str, html: str) -> Optional[bool]:
        """Envia via Azure Communication Services. Retorna None se nao configurado."""
        conn = getattr(settings, "acs_email_connection_string", None)
        sender = getattr(settings, "acs_email_sender", None)
        if not conn or not sender:
            return None
        try:
            # Import local: dependencia opcional (so instalada quando ACS for usado)
            from azure.communication.email import EmailClient

            client = EmailClient.from_connection_string(conn)
            message = {
                "senderAddress": sender,
                "recipients": {"to": [{"address": to_email}]},
                "content": {"subject": subject, "html": html},
            }
            poller = client.begin_send(message)
            result = poller.result()
            ok = (result.get("status") or "").lower() == "succeeded"
            logger.info(f"ACS email para {to_email}: {result.get('status')}")
            return ok
        except Exception as e:
            logger.error(f"ACS email falhou: {e}")
            return False

    async def _send_resend(self, to_email: str, subject: str, html: str) -> bool:
        api_key = settings.resend_api_key
        if not api_key:
            logger.warning("RESEND_API_KEY nao configurada — e-mail do no nao enviado")
            return False
        from_email_addr = settings.email_from or "onboarding@resend.dev"
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                res = await client.post(
                    "https://api.resend.com/emails",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "from": f"IT Valley School <{from_email_addr}>",
                        "to": [to_email],
                        "subject": subject,
                        "html": html,
                    },
                )
                if res.status_code not in (200, 201):
                    logger.error(f"Resend email error: {res.status_code} {res.text[:200]}")
                    return False
            logger.info(f"Resend email enviado para {to_email}")
            return True
        except Exception as e:
            logger.error(f"Resend email falhou: {e}")
            return False

    async def send_node_email(
        self,
        *,
        to_email: str,
        subject_template: str,
        body_template: str,
        lead_values: dict,
    ) -> dict:
        """Envia o e-mail do no com placeholders resolvidos ({{nome}}, {{email}}...)."""
        if not to_email or "@" not in to_email:
            return {"success": False, "error": "email do lead invalido"}

        subject = _resolve(subject_template, lead_values) or "IT Valley School"
        body = _resolve(body_template, lead_values)
        html = self._build_html(body)

        try:
            acs_result = await self._send_acs(to_email, subject, html)
            if acs_result is not None:
                return {"success": acs_result, "provider": "acs"}
            sent = await self._send_resend(to_email, subject, html)
            return {"success": sent, "provider": "resend"}
        except Exception as e:
            logger.error(f"Email do no falhou (nao-fatal): {e}")
            return {"success": False, "error": str(e)}
