class FlowMapper:
    """Converte documento MongoDB -> dict de resposta.

    So conversao, nunca valida.
    """

    @staticmethod
    def to_response(doc: dict) -> dict:
        return {
            "_id": str(doc["_id"]),
            "tenant_id": doc.get("tenant_id", ""),
            "name": doc.get("name", ""),
            "slug": doc.get("slug", ""),
            "status": doc.get("status", "draft"),
            "version": doc.get("version", 1),
            "nodes": doc.get("nodes", []),
            "edges": doc.get("edges", []),
            "pricing_csv": doc.get("pricing_csv", ""),
            "activecampaign_list_id": doc.get("activecampaign_list_id", ""),
            "activecampaign_list_name": doc.get("activecampaign_list_name", ""),
            "theme_color": doc.get("theme_color", "violet"),
            "page_template": doc.get("page_template", "centered"),
            "page_content": doc.get("page_content", {}),
            "scheduling_config": doc.get("scheduling_config"),
            "meeting_link_override": doc.get("meeting_link_override"),
            "gcal_event_title": doc.get("gcal_event_title"),
            "gcal_calendar_id": doc.get("gcal_calendar_id"),
            "email_config": doc.get("email_config"),
            "ui_texts": doc.get("ui_texts"),
            "created_at": doc.get("created_at", ""),
            "updated_at": doc.get("updated_at", ""),
        }

    @staticmethod
    def to_summary(doc: dict) -> dict:
        return {
            "_id": str(doc["_id"]),
            "tenant_id": doc.get("tenant_id", ""),
            "name": doc.get("name", ""),
            "slug": doc.get("slug", ""),
            "status": doc.get("status", "draft"),
            "version": doc.get("version", 1),
            "node_count": len(doc.get("nodes", [])),
            "created_at": doc.get("created_at", ""),
            "updated_at": doc.get("updated_at", ""),
        }
