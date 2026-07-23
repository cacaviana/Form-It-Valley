from bson import ObjectId
from typing import Optional
from data.interfaces.base_repository import BaseRepository
from config.database import mongodb_client


def _tenant_filter(tenant_id: Optional[str]) -> dict:
    """Filtro de tenant — obrigatorio nas rotas autenticadas.

    tenant_id=None so e permitido em lookups de resolucao publica
    (ex: buscar flow por slug/id para descobrir a QUAL tenant ele pertence).
    """
    return {"tenant_id": tenant_id} if tenant_id else {}


class FlowRepository(BaseRepository):

    def __init__(self):
        self._collection_name = "flows"

    @property
    def _collection(self):
        return mongodb_client.database[self._collection_name]

    async def find_all(self, tenant_id: Optional[str] = None) -> list[dict]:
        query = {"active": {"$ne": False}, **_tenant_filter(tenant_id)}
        cursor = self._collection.find(query).sort("updated_at", -1)
        return await cursor.to_list(length=100)

    async def find_by_id(self, id: str, tenant_id: Optional[str] = None) -> Optional[dict]:
        if not ObjectId.is_valid(id):
            return None
        # Filtra flows soft-deleted (active=False)
        query = {"_id": ObjectId(id), "active": {"$ne": False}, **_tenant_filter(tenant_id)}
        return await self._collection.find_one(query)

    async def find_by_slug(self, slug: str, tenant_id: Optional[str] = None) -> Optional[dict]:
        # Filtra flows soft-deleted (active=False)
        query = {"slug": slug, "active": {"$ne": False}, **_tenant_filter(tenant_id)}
        return await self._collection.find_one(query)

    async def count_slugs_starting_with(self, slug_prefix: str) -> int:
        """Conta quantos flows tem slug que comeca com o prefixo (para gerar slug unico).

        Global (sem tenant) — o slug e a chave publica do formulario e precisa
        ser unico no sistema inteiro.
        """
        return await self._collection.count_documents({
            "slug": {"$regex": f"^{slug_prefix}(-\\d+)?$"}
        })

    async def insert(self, document: dict) -> dict:
        result = await self._collection.insert_one(document)
        document["_id"] = result.inserted_id
        return document

    async def update(self, id: str, data: dict, tenant_id: Optional[str] = None) -> Optional[dict]:
        if not ObjectId.is_valid(id):
            return None
        result = await self._collection.find_one_and_update(
            {"_id": ObjectId(id), **_tenant_filter(tenant_id)},
            {"$set": data},
            return_document=True,
        )
        return result

    async def delete(self, id: str, tenant_id: Optional[str] = None) -> bool:
        """Soft delete — marca active=False em vez de remover."""
        if not ObjectId.is_valid(id):
            return False
        result = await self._collection.update_one(
            {"_id": ObjectId(id), **_tenant_filter(tenant_id)},
            {"$set": {"active": False}},
        )
        return result.modified_count > 0
