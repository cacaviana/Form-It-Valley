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
