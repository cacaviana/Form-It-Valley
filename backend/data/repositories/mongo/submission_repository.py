from bson import ObjectId
from typing import Optional
from data.interfaces.base_repository import BaseRepository
from config.database import mongodb_client


class SubmissionRepository(BaseRepository):

    def __init__(self):
        self._collection_name = "submissions"

    @property
    def _collection(self):
        return mongodb_client.database[self._collection_name]

    async def find_all(self) -> list[dict]:
        cursor = self._collection.find().sort("created_at", -1)
        return await cursor.to_list(length=200)

    async def find_by_flow(self, flow_id: str) -> list[dict]:
        cursor = self._collection.find({"flow_id": flow_id}).sort("created_at", -1)
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
        result = await self._collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": data},
            return_document=True,
        )
        return result

    async def delete(self, id: str) -> bool:
        if not ObjectId.is_valid(id):
            return False
        result = await self._collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0
