class BlacklistMapper:
    """Converte documento MongoDB -> dict de resposta. So conversao."""

    @staticmethod
    def to_metadata(doc: dict) -> dict:
        """Resposta SEM as entries (privacidade — nao expor a lista)."""
        return {
            "id": str(doc["_id"]),
            "tenant_id": doc.get("tenant_id", ""),
            "scope_type": doc.get("scope_type", "flow"),
            "scope_id": doc.get("scope_id", ""),
            "total_entries": doc.get("total_entries", 0),
            "csv_uploaded_at": doc.get("csv_uploaded_at"),
            "csv_uploaded_by": doc.get("csv_uploaded_by"),
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at"),
        }


class BlockedAttemptMapper:
    @staticmethod
    def to_response(doc: dict) -> dict:
        return {
            "id": str(doc["_id"]),
            "tenant_id": doc.get("tenant_id", ""),
            "flow_id": doc.get("flow_id", ""),
            "email": doc.get("email"),
            "phone": doc.get("phone"),
            "matched_field": doc.get("matched_field", ""),
            "blocked_at": doc.get("blocked_at", ""),
        }
