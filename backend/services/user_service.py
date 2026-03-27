import hashlib
import secrets
import logging
from typing import Optional
from config.database import mongodb_client

logger = logging.getLogger(__name__)

# Paginas disponiveis no sistema
AVAILABLE_PAGES = [
    {"key": "scheduling", "label": "Agendamento"},
    {"key": "flows", "label": "Fluxos / Questionarios"},
    {"key": "settings", "label": "Configuracoes"},
    {"key": "users", "label": "Gestao de Usuarios"},
]


def _hash_password(password: str, salt: str = "") -> tuple[str, str]:
    """Hash password com salt. Retorna (hash, salt)."""
    if not salt:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000).hex()
    return hashed, salt


def _verify_password(password: str, hashed: str, salt: str) -> bool:
    """Verifica se a senha bate com o hash."""
    check, _ = _hash_password(password, salt)
    return check == hashed


class UserService:
    """CRUD de usuarios com permissoes."""

    def __init__(self):
        self._collection_name = "users"

    @property
    def _collection(self):
        return mongodb_client.database[self._collection_name]

    async def list_all(self) -> list[dict]:
        """Lista todos os usuarios ativos (sem senha)."""
        docs = await self._collection.find({"active": {"$ne": False}}).sort("created_at", -1).to_list(200)
        return [_sanitize(doc) for doc in docs]

    async def get_by_id(self, user_id: str) -> Optional[dict]:
        """Busca usuario por ID."""
        from bson import ObjectId
        try:
            doc = await self._collection.find_one({"_id": ObjectId(user_id)})
        except Exception:
            return None
        if not doc:
            return None
        return _sanitize(doc)

    async def get_by_email(self, email: str) -> Optional[dict]:
        """Busca usuario por email (inclui senha para autenticacao)."""
        doc = await self._collection.find_one({"email": email})
        return doc

    async def authenticate(self, email: str, password: str) -> Optional[dict]:
        """Autentica usuario. Retorna dados (sem senha) ou None."""
        doc = await self.get_by_email(email)
        if not doc:
            return None
        if not doc.get("active", True):
            return None
        if not _verify_password(password, doc.get("password_hash", ""), doc.get("password_salt", "")):
            return None
        return _sanitize(doc)

    async def create(self, data: dict) -> dict:
        """Cria novo usuario."""
        existing = await self.get_by_email(data["email"])
        if existing:
            raise ValueError("Email ja cadastrado")

        password_hash, password_salt = _hash_password(data["password"])

        from datetime import datetime, timezone
        doc = {
            "name": data["name"],
            "email": data["email"],
            "password_hash": password_hash,
            "password_salt": password_salt,
            "permissions": data.get("permissions", []),
            "active": data.get("active", True),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        result = await self._collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return _sanitize(doc)

    async def update(self, user_id: str, data: dict) -> Optional[dict]:
        """Atualiza usuario."""
        from bson import ObjectId
        try:
            oid = ObjectId(user_id)
        except Exception:
            return None

        update_fields: dict = {}
        if "name" in data:
            update_fields["name"] = data["name"]
        if "email" in data:
            update_fields["email"] = data["email"]
        if "permissions" in data:
            update_fields["permissions"] = data["permissions"]
        if "active" in data:
            update_fields["active"] = data["active"]
        if "password" in data and data["password"]:
            ph, ps = _hash_password(data["password"])
            update_fields["password_hash"] = ph
            update_fields["password_salt"] = ps

        if not update_fields:
            return await self.get_by_id(user_id)

        await self._collection.update_one({"_id": oid}, {"$set": update_fields})
        return await self.get_by_id(user_id)

    async def delete(self, user_id: str) -> bool:
        """Soft delete — marca active=False."""
        from bson import ObjectId
        try:
            result = await self._collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"active": False}},
            )
            return result.modified_count > 0
        except Exception:
            return False

    def get_available_pages(self) -> list[dict]:
        """Retorna paginas disponiveis para permissao."""
        return AVAILABLE_PAGES


def _sanitize(doc: dict) -> dict:
    """Remove campos sensíveis e converte _id."""
    return {
        "id": str(doc["_id"]),
        "name": doc.get("name", ""),
        "email": doc.get("email", ""),
        "permissions": doc.get("permissions", []),
        "active": doc.get("active", True),
        "created_at": doc.get("created_at", ""),
    }
