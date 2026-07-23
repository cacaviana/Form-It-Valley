from bson import ObjectId
from typing import Optional
from data.interfaces.base_repository import BaseRepository
from config.database import mongodb_client


def _tenant_filter(tenant_id: Optional[str]) -> dict:
    return {"tenant_id": tenant_id} if tenant_id else {}


class SubmissionRepository(BaseRepository):

    def __init__(self):
        self._collection_name = "submissions"

    @property
    def _collection(self):
        return mongodb_client.database[self._collection_name]

    async def find_all(self, tenant_id: Optional[str] = None) -> list[dict]:
        query = {"hidden": {"$ne": True}, **_tenant_filter(tenant_id)}
        cursor = self._collection.find(query).sort("created_at", -1)
        return await cursor.to_list(length=200)

    async def find_by_flow(self, flow_id: str, tenant_id: Optional[str] = None) -> list[dict]:
        query = {"flow_id": flow_id, "hidden": {"$ne": True}, **_tenant_filter(tenant_id)}
        cursor = self._collection.find(query).sort("created_at", -1)
        return await cursor.to_list(length=200)

    async def find_by_id(self, id: str, tenant_id: Optional[str] = None) -> Optional[dict]:
        if not ObjectId.is_valid(id):
            return None
        return await self._collection.find_one(
            {"_id": ObjectId(id), **_tenant_filter(tenant_id)}
        )

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
        if not ObjectId.is_valid(id):
            return False
        result = await self._collection.delete_one(
            {"_id": ObjectId(id), **_tenant_filter(tenant_id)}
        )
        return result.deleted_count > 0

    async def hide(self, id: str, tenant_id: Optional[str] = None) -> bool:
        """Soft-delete: marca como oculta, sem remover do banco."""
        if not ObjectId.is_valid(id):
            return False
        result = await self._collection.update_one(
            {"_id": ObjectId(id), **_tenant_filter(tenant_id)},
            {"$set": {"hidden": True}},
        )
        return result.matched_count > 0
