from bson import ObjectId
from typing import Optional
from data.interfaces.base_repository import BaseRepository
from config.database import mongodb_client


class BlacklistRepository(BaseRepository):
    """Acesso a collection 'blacklists'.

    Modelo: 1 documento por (scope_type + scope_id). Upload novo substitui o anterior.
    Reusavel: scope_type pode ser 'flow' (por formulario) ou 'tenant' (global).
    """

    def __init__(self):
        self._collection_name = "blacklists"

    @property
    def _collection(self):
        return mongodb_client.database[self._collection_name]

    async def find_all(self) -> list[dict]:
        cursor = self._collection.find().sort("updated_at", -1)
        return await cursor.to_list(length=200)

    async def find_by_id(self, id: str) -> Optional[dict]:
        if not ObjectId.is_valid(id):
            return None
        return await self._collection.find_one({"_id": ObjectId(id)})

    async def insert(self, document: dict) -> dict:
        result = await self._collection.insert_one(document)
        document["_id"] = result.inserted_id
        return document

    async def update(self, id: str, data: dict) -> Optional[dict]:
        if not ObjectId.is_valid(id):
            return None
        await self._collection.update_one({"_id": ObjectId(id)}, {"$set": data})
        return await self.find_by_id(id)

    async def delete(self, id: str) -> bool:
        if not ObjectId.is_valid(id):
            return False
        result = await self._collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0

    # ------- metodos de dominio -------

    async def find_by_scope(self, scope_type: str, scope_id: str) -> Optional[dict]:
        return await self._collection.find_one({
            "scope_type": scope_type,
            "scope_id": scope_id,
        })

    async def upsert(self, doc: dict) -> dict:
        """Insere ou substitui blacklist do mesmo escopo."""
        filter_ = {
            "tenant_id": doc["tenant_id"],
            "scope_type": doc["scope_type"],
            "scope_id": doc["scope_id"],
        }
        existing = await self._collection.find_one(filter_)
        if existing:
            doc["created_at"] = existing.get("created_at", doc["created_at"])
            await self._collection.replace_one({"_id": existing["_id"]}, doc)
            doc["_id"] = existing["_id"]
        else:
            result = await self._collection.insert_one(doc)
            doc["_id"] = result.inserted_id
        return doc

    async def delete_by_scope(self, scope_type: str, scope_id: str) -> int:
        result = await self._collection.delete_many({
            "scope_type": scope_type,
            "scope_id": scope_id,
        })
        return result.deleted_count
