from bson import ObjectId
from typing import Optional
from data.interfaces.base_repository import BaseRepository
from config.database import mongodb_client


class FlowRepository(BaseRepository):

    def __init__(self):
        self._collection_name = "flows"

    @property
    def _collection(self):
        return mongodb_client.database[self._collection_name]

    async def find_all(self) -> list[dict]:
        cursor = self._collection.find({"active": {"$ne": False}}).sort("updated_at", -1)
        return await cursor.to_list(length=100)

    async def find_by_id(self, id: str) -> Optional[dict]:
        if not ObjectId.is_valid(id):
            return None
        return await self._collection.find_one({"_id": ObjectId(id)})

    async def find_by_slug(self, slug: str) -> Optional[dict]:
        return await self._collection.find_one({"slug": slug})

    async def count_slugs_starting_with(self, slug_prefix: str) -> int:
        """Conta quantos flows tem slug que comeca com o prefixo (para gerar slug unico)."""
        return await self._collection.count_documents({
            "slug": {"$regex": f"^{slug_prefix}(-\\d+)?$"}
        })

    async def insert(self, document: dict) -> dict:
        result = await self._collection.insert_one(document)
        document["_id"] = result.inserted_id
        return document

    async def update(self, id: str, data: dict) -> Optional[dict]:
        if not ObjectId.is_valid(id):
            return None
        result = await self._collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": data},
            return_document=True,
        )
        return result

    async def delete(self, id: str) -> bool:
        """Soft delete — marca active=False em vez de remover."""
        if not ObjectId.is_valid(id):
            return False
        result = await self._collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"active": False}},
        )
        return result.modified_count > 0
