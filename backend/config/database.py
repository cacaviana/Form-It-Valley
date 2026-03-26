from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from config.settings import settings
import certifi


class MongoDBClient:

    def __init__(self):
        self._client: Optional[AsyncIOMotorClient] = None

    @property
    def client(self) -> AsyncIOMotorClient:
        if self._client is None:
            self._client = AsyncIOMotorClient(
                settings.mongodb_uri,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=20000,
                connectTimeoutMS=20000,
                socketTimeoutMS=20000,
            )
        return self._client

    @property
    def database(self):
        return self.client[settings.mongodb_database]

    async def close(self):
        if self._client:
            self._client.close()


mongodb_client = MongoDBClient()


async def get_database():
    return mongodb_client.database
