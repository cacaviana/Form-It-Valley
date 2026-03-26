class SubmissionMapper:
    """Converte documento MongoDB -> dict de resposta. So conversao."""

    @staticmethod
    def to_response(doc: dict) -> dict:
        return {
            "id": str(doc["_id"]),
            "tenant_id": doc.get("tenant_id", ""),
            "flow_id": doc.get("flow_id", ""),
            "flow_slug": doc.get("flow_slug", ""),
            "client_name": doc.get("client_name", ""),
            "client_email": doc.get("client_email", ""),
            "client_phone": doc.get("client_phone"),
            "client_address": doc.get("client_address"),
            "answers": doc.get("answers", []),
            "end_node_id": doc.get("end_node_id", ""),
            "end_type": doc.get("end_type", ""),
            "quote_text": doc.get("quote_text"),
            "quote_data": doc.get("quote_data"),
            "status": doc.get("status", "pending"),
            "created_at": doc.get("created_at", ""),
        }

    @staticmethod
    def to_summary(doc: dict) -> dict:
        return {
            "id": str(doc["_id"]),
            "tenant_id": doc.get("tenant_id", ""),
            "flow_id": doc.get("flow_id", ""),
            "flow_slug": doc.get("flow_slug", ""),
            "client_name": doc.get("client_name", ""),
            "client_email": doc.get("client_email", ""),
            "end_type": doc.get("end_type", ""),
            "status": doc.get("status", "pending"),
            "has_quote": doc.get("quote_text") is not None,
            "created_at": doc.get("created_at", ""),
        }
