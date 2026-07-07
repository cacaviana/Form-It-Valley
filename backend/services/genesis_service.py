import logging
from typing import Optional

import httpx

from config.settings import settings

logger = logging.getLogger(__name__)


class GenesisService:
    """Envia leads pro Genesis (CRM) via webhook de integracao tipo 'forms'.

    Fase 1b substituicao ActiveCampaign (2026-07-06). Fire-and-forget:
    NUNCA levanta exception — falha vira log de erro e o fluxo do lead segue.
    URL completa (com token) vem de GENESIS_WEBHOOK_URL no ambiente.
    """

    def __init__(self):
        self._webhook_url = settings.genesis_webhook_url or ""

    def _configured(self) -> bool:
        return bool(self._webhook_url)

    async def send_lead(
        self,
        *,
        evento: str,  # "lead_iniciado" | "agendamento_confirmado"
        nome: str,
        email: str,
        telefone: str = "",
        flow_slug: str = "",
        utm_source: Optional[str] = None,
        utm_medium: Optional[str] = None,
        utm_campaign: Optional[str] = None,
        agendamento_data: Optional[str] = None,
        agendamento_hora: Optional[str] = None,
    ) -> dict:
        if not self._configured():
            return {"success": False, "error": "Genesis nao configurado"}

        payload = {
            "evento": evento,
            "nome": nome,
            "email": email,
            "telefone": telefone,
            "flow_slug": flow_slug,
            "utm_source": utm_source,
            "utm_medium": utm_medium,
            "utm_campaign": utm_campaign,
        }
        if agendamento_data:
            payload["agendamento"] = {"data": agendamento_data, "hora": agendamento_hora or ""}

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                res = await client.post(self._webhook_url, json=payload)
                if res.status_code != 200:
                    logger.error(f"Genesis webhook error: {res.status_code} {res.text[:300]}")
                    return {"success": False, "error": f"status {res.status_code}"}
                data = res.json()
                logger.info(
                    f"Genesis: lead {email} enviado ({evento}) — evento_id={data.get('evento_id')} status={data.get('status')}"
                )
                return {"success": True, **data}
        except Exception as e:
            logger.error(f"Genesis webhook falhou (nao-fatal): {e}")
            return {"success": False, "error": str(e)}
