import re
import httpx
import logging
from typing import Optional
from config.settings import settings

logger = logging.getLogger(__name__)

GRAPH_API_URL = "https://graph.facebook.com/v21.0"


class WhatsAppService:
    """Integracao direta com a API do Meta WhatsApp Business."""

    def __init__(self):
        self._access_token = settings.whatsapp_access_token or ""
        self._phone_number_id = settings.whatsapp_phone_number_id or ""
        self._waba_id = settings.whatsapp_waba_id or ""

    def _configured(self) -> bool:
        return bool(self._access_token and self._phone_number_id)

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

    async def list_templates(self) -> list[dict]:
        """Lista templates aprovados do WhatsApp Business."""
        if not self._access_token or not self._waba_id:
            return []

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                res = await client.get(
                    f"{GRAPH_API_URL}/{self._waba_id}/message_templates",
                    params={"limit": 100},
                    headers=self._headers(),
                )

            if res.status_code != 200:
                logger.error(f"WhatsApp templates error: {res.status_code} {res.text}")
                return []

            data = res.json()
            templates = []
            for t in data.get("data", []):
                if t.get("status") != "APPROVED":
                    continue
                body_component = next(
                    (c for c in t.get("components", []) if c.get("type") == "BODY"),
                    None,
                )
                body_text = body_component.get("text", "") if body_component else ""
                var_count = len(re.findall(r"\{\{\d+\}\}", body_text))
                templates.append({
                    "name": t.get("name", ""),
                    "language": t.get("language", ""),
                    "category": t.get("category", ""),
                    "body": body_text,
                    "variableCount": var_count,
                })
            return templates

        except Exception as e:
            logger.error(f"WhatsApp templates fetch error: {e}")
            return []

    async def send_template_message(
        self,
        to_phone: str,
        template_name: str,
        language: str = "pt_BR",
        variables: Optional[list[str]] = None,
    ) -> dict:
        """Envia mensagem de template via API direta do Meta."""
        if not self._configured():
            return {"success": False, "error": "WhatsApp not configured"}

        # Montar componentes com variaveis
        components = []
        if variables and len(variables) > 0:
            parameters = [
                {"type": "text", "text": v.replace("\n", " ").replace("\t", " ")}
                for v in variables
            ]
            components.append({
                "type": "body",
                "parameters": parameters,
            })

        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language},
                "components": components,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                res = await client.post(
                    f"{GRAPH_API_URL}/{self._phone_number_id}/messages",
                    headers=self._headers(),
                    json=payload,
                )

            if res.status_code in (200, 201):
                result = res.json()
                message_id = result.get("messages", [{}])[0].get("id", "")
                logger.info(f"WhatsApp enviado para {to_phone} — message_id: {message_id}")
                return {"success": True, "message_id": message_id}
            else:
                logger.error(f"WhatsApp send error: {res.status_code} {res.text}")
                return {"success": False, "error": f"Meta API error: {res.status_code}"}

        except Exception as e:
            logger.error(f"WhatsApp send error: {e}")
            return {"success": False, "error": str(e)}
