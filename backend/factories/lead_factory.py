from datetime import datetime, timezone


class LeadFactory:
    """Cria documentos de lead com regras de negocio."""

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @classmethod
    def create_new(cls, data: dict) -> dict:
        """Cria lead a partir dos dados do formulario inicial."""
        return {
            "tenant_id": data.get("tenant_id", "tenant_1"),
            "flow_id": data["flow_id"],
            "flow_slug": data["flow_slug"],
            "client_name": data["client_name"],
            "client_email": data["client_email"],
            "client_phone": data.get("client_phone"),
            "client_phone_country_code": data.get("client_phone_country_code"),
            "client_address": data.get("client_address"),
            "status": "started",
            "activecampaign_synced": False,
            "created_at": cls._now_iso(),
        }
