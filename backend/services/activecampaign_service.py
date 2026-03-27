import httpx
import logging
from config.settings import settings

logger = logging.getLogger(__name__)


class ActiveCampaignService:
    """Integracao com ActiveCampaign — lista listas e cadastra contatos."""

    def __init__(self):
        self._api_url = settings.activecampaign_api_url or ""
        self._api_key = settings.activecampaign_api_key or ""

    def _headers(self) -> dict:
        return {
            "Api-Token": self._api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _configured(self) -> bool:
        return bool(self._api_url and self._api_key)

    async def list_lists(self) -> list[dict]:
        """Retorna todas as listas do ActiveCampaign."""
        if not self._configured():
            return []

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                res = await client.get(
                    f"{self._api_url}/api/3/lists",
                    params={"limit": 100},
                    headers=self._headers(),
                )

            if res.status_code != 200:
                logger.error(f"ActiveCampaign lists error: {res.status_code} {res.text}")
                return []

            data = res.json()
            return [
                {
                    "id": l["id"],
                    "name": l["name"],
                    "cdate": l.get("cdate", ""),
                    "subscriber_count": int(l.get("subscriber_count", 0)),
                }
                for l in data.get("lists", [])
            ]
        except Exception as e:
            logger.error(f"ActiveCampaign lists fetch error: {e}")
            return []

    async def add_contact_to_list(
        self,
        email: str,
        first_name: str,
        last_name: str = "",
        phone: str = "",
        list_id: str = "",
    ) -> dict:
        """Cria/atualiza contato no AC e adiciona a uma lista."""
        if not self._configured():
            return {"success": False, "error": "ActiveCampaign not configured"}

        if not list_id:
            return {"success": False, "error": "list_id is required"}

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                # 1. Criar/atualizar contato via sync
                contact_res = await client.post(
                    f"{self._api_url}/api/3/contact/sync",
                    headers=self._headers(),
                    json={
                        "contact": {
                            "email": email,
                            "firstName": first_name,
                            "lastName": last_name,
                            "phone": phone,
                        }
                    },
                )

                if contact_res.status_code not in (200, 201):
                    logger.error(f"AC contact sync error: {contact_res.status_code} {contact_res.text}")
                    return {"success": False, "error": f"Contact sync failed: {contact_res.status_code}"}

                contact_data = contact_res.json()
                contact_id = contact_data.get("contact", {}).get("id")

                if not contact_id:
                    return {"success": False, "error": "No contact ID returned"}

                # 2. Adicionar contato a lista
                list_res = await client.post(
                    f"{self._api_url}/api/3/contactLists",
                    headers=self._headers(),
                    json={
                        "contactList": {
                            "list": list_id,
                            "contact": contact_id,
                            "status": 1,  # 1 = subscribed
                        }
                    },
                )

                if list_res.status_code not in (200, 201):
                    logger.error(f"AC list subscribe error: {list_res.status_code} {list_res.text}")
                    return {
                        "success": False,
                        "contact_id": contact_id,
                        "error": f"List subscribe failed: {list_res.status_code}",
                    }

            logger.info(f"ActiveCampaign: contact {email} (ID: {contact_id}) added to list {list_id}")
            return {"success": True, "contact_id": contact_id}

        except Exception as e:
            logger.error(f"ActiveCampaign error: {e}")
            return {"success": False, "error": str(e)}
