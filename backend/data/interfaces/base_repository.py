from abc import ABC, abstractmethod
from typing import Optional


class BaseRepository(ABC):

    @abstractmethod
    async def find_all(self) -> list[dict]:
        ...

    @abstractmethod
    async def find_by_id(self, id: str) -> Optional[dict]:
        ...

    @abstractmethod
    async def insert(self, document: dict) -> dict:
        ...

    @abstractmethod
    async def update(self, id: str, data: dict) -> Optional[dict]:
        ...

    @abstractmethod
    async def delete(self, id: str) -> bool:
        ...
