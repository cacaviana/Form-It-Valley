from datetime import datetime, timezone


class SubmissionFactory:
    """Cria documentos de submission com regras de negocio."""

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @classmethod
    def create_new(cls, data: dict, end_node: dict) -> dict:
        """Cria submission a partir dos dados do request + info do end node."""

        end_type = end_node.get("data", {}).get("endType", "thank_you")

        return {
            "tenant_id": data.get("tenant_id", "tenant_1"),
            "flow_id": data["flow_id"],
            "flow_slug": data["flow_slug"],
            "client_name": data["client_name"],
            "client_email": data["client_email"],
            "client_phone": data.get("client_phone"),
            "client_address": data.get("client_address"),
            "answers": data["answers"],
            "end_node_id": data["end_node_id"],
            "end_type": end_type,
            "business_context": end_node.get("data", {}).get("businessContext", ""),
            "ai_instruction": end_node.get("data", {}).get("aiInstruction", ""),
            "quote_text": None,
            "status": "pending",
            "created_at": cls._now_iso(),
        }
