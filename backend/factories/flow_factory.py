import re
from datetime import datetime, timezone


class FlowFactory:
    """Cria documentos de flow com regras de negocio.

    Responsabilidades:
    - Gerar slug a partir do nome
    - Definir valores default (version, status, timestamps)
    - Validar invariantes (max nodes, start node obrigatorio)
    """

    MAX_NODES = 50

    @staticmethod
    def _generate_slug(name: str) -> str:
        slug = name.lower().strip()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s]+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        return slug.strip('-')

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @classmethod
    def create_new(cls, data: dict) -> dict:
        nodes = data.get("nodes", [])

        if len(nodes) > cls.MAX_NODES:
            raise ValueError(f"Flow nao pode ter mais de {cls.MAX_NODES} nos")

        has_start = any(n.get("type") == "start" for n in nodes)
        if not has_start:
            raise ValueError("Flow precisa ter pelo menos um no de inicio (start)")

        now = cls._now_iso()
        slug = data.get("slug") or cls._generate_slug(data["name"])

        doc = {
            "tenant_id": data.get("tenant_id", "tenant_1"),
            "name": data["name"],
            "slug": slug,
            "status": data.get("status", "draft"),
            "version": 1,
            "nodes": nodes,
            "edges": data.get("edges", []),
            "created_at": now,
            "updated_at": now,
        }
        if data.get("pricing_csv") is not None:
            doc["pricing_csv"] = data["pricing_csv"]
        if data.get("activecampaign_list_id") is not None:
            doc["activecampaign_list_id"] = data["activecampaign_list_id"]
            doc["activecampaign_list_name"] = data.get("activecampaign_list_name", "")
        doc["theme_color"] = data.get("theme_color", "violet")
        return doc

    @classmethod
    def create_update(cls, existing: dict, data: dict) -> dict:
        nodes = data.get("nodes", existing.get("nodes", []))

        if len(nodes) > cls.MAX_NODES:
            raise ValueError(f"Flow nao pode ter mais de {cls.MAX_NODES} nos")

        has_start = any(n.get("type") == "start" for n in nodes)
        if not has_start:
            raise ValueError("Flow precisa ter pelo menos um no de inicio (start)")

        slug = data.get("slug") or cls._generate_slug(data["name"])

        update_doc = {
            "name": data["name"],
            "slug": slug,
            "status": data.get("status", existing.get("status", "draft")),
            "version": existing.get("version", 0) + 1,
            "nodes": nodes,
            "edges": data.get("edges", existing.get("edges", [])),
            "updated_at": cls._now_iso(),
        }
        # Preserve or update pricing_csv
        if data.get("pricing_csv") is not None:
            update_doc["pricing_csv"] = data["pricing_csv"]
        elif existing.get("pricing_csv"):
            update_doc["pricing_csv"] = existing["pricing_csv"]
        # Preserve or update activecampaign
        ac_id = data.get("activecampaign_list_id")
        if ac_id is not None:
            # Frontend enviou o campo (pode ser "" para limpar ou "123" para setar)
            update_doc["activecampaign_list_id"] = ac_id
            update_doc["activecampaign_list_name"] = data.get("activecampaign_list_name", "")
        elif existing.get("activecampaign_list_id"):
            update_doc["activecampaign_list_id"] = existing["activecampaign_list_id"]
            update_doc["activecampaign_list_name"] = existing.get("activecampaign_list_name", "")
        update_doc["theme_color"] = data.get("theme_color") or existing.get("theme_color", "violet")
        return update_doc
