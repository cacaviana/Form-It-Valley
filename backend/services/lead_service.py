from data.repositories.mongo.lead_repository import LeadRepository
from data.repositories.mongo.flow_repository import FlowRepository
from factories.lead_factory import LeadFactory
from services.activecampaign_service import ActiveCampaignService
import logging

logger = logging.getLogger(__name__)


class LeadService:
    """Orquestra criacao de leads — salva no MongoDB e sincroniza com ActiveCampaign."""

    def __init__(self):
        self._repo = LeadRepository()
        self._flow_repo = FlowRepository()
        self._ac = ActiveCampaignService()

    async def create(self, data: dict) -> dict:
        """Cria ou atualiza lead. Se ja existe com mesmo email+flow, atualiza."""
        existing = await self._repo.find_by_email_and_flow(
            data["client_email"], data["flow_slug"]
        )

        if existing:
            update_data = {
                "client_name": data["client_name"],
                "client_phone": data.get("client_phone"),
                "client_phone_country_code": data.get("client_phone_country_code"),
                "client_address": data.get("client_address"),
                "status": "started",
            }
            doc = await self._repo.update(str(existing["_id"]), update_data)
        else:
            doc = LeadFactory.create_new(data)
            doc = await self._repo.insert(doc)

        # Sincronizar com ActiveCampaign se tiver list_id
        ac_list_id = data.get("activecampaign_list_id")
        if ac_list_id:
            try:
                name_parts = (data.get("client_name") or "").strip().split(" ")
                phone = data.get("client_phone") or ""
                country_code = data.get("client_phone_country_code") or ""
                full_phone = f"+{country_code}{phone}" if country_code and phone else phone

                ac_result = await self._ac.add_contact_to_list(
                    email=data["client_email"],
                    first_name=name_parts[0] if name_parts else "",
                    last_name=" ".join(name_parts[1:]) if len(name_parts) > 1 else "",
                    phone=full_phone,
                    list_id=ac_list_id,
                )
                ac_synced = ac_result.get("success", False)
                await self._repo.update(str(doc["_id"]), {"activecampaign_synced": ac_synced})
                doc["activecampaign_synced"] = ac_synced
            except Exception as e:
                logger.error(f"Erro ao sincronizar lead com ActiveCampaign: {e}")

        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)
        return doc
