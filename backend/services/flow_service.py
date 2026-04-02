from typing import Optional
from data.repositories.mongo.flow_repository import FlowRepository
from factories.flow_factory import FlowFactory
from mappers.flow_mapper import FlowMapper


class FlowService:
    """Camada opaca — orquestra Factory, Repository e Mapper.

    NAO conhece campos do flow. Delega tudo.
    """

    def __init__(self):
        self._repository = FlowRepository()
        self._factory = FlowFactory
        self._mapper = FlowMapper

    async def list_all(self) -> dict:
        docs = await self._repository.find_all()
        summaries = [self._mapper.to_summary(doc) for doc in docs]
        return {"flows": summaries, "total": len(summaries)}

    async def get_by_id(self, id: str) -> Optional[dict]:
        doc = await self._repository.find_by_id(id)
        if not doc:
            return None
        return self._mapper.to_response(doc)

    async def get_by_slug(self, slug: str) -> Optional[dict]:
        doc = await self._repository.find_by_slug(slug)
        if not doc:
            return None
        return self._mapper.to_response(doc)

    async def create(self, data: dict) -> dict:
        flow_doc = self._factory.create_new(data)

        # Garantir slug unico — se ja existe, adiciona sufixo numerico
        base_slug = flow_doc["slug"]
        existing = await self._repository.find_by_slug(base_slug)
        if existing:
            count = await self._repository.count_slugs_starting_with(base_slug)
            flow_doc["slug"] = f"{base_slug}-{count}"

        saved = await self._repository.insert(flow_doc)
        return self._mapper.to_response(saved)

    async def update(self, id: str, data: dict) -> Optional[dict]:
        existing = await self._repository.find_by_id(id)
        if not existing:
            return None
        update_data = self._factory.create_update(existing, data)
        updated = await self._repository.update(id, update_data)
        if not updated:
            return None
        return self._mapper.to_response(updated)

    async def delete(self, id: str) -> bool:
        return await self._repository.delete(id)
