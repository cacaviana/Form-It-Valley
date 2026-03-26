from fastapi import APIRouter
from pydantic import BaseModel
from config.database import mongodb_client

router = APIRouter(prefix="/api/settings", tags=["settings"])

COLLECTION = "settings"
DOC_ID = "ai_settings"

MODELS = {
    "anthropic": [
        {"id": "claude-sonnet-4-20250514", "label": "Claude Sonnet 4"},
        {"id": "claude-opus-4-6", "label": "Claude Opus 4.6"},
    ],
    "openai": [
        {"id": "gpt-4o", "label": "GPT-4o"},
        {"id": "gpt-4.5-preview", "label": "GPT-4.5"},
    ],
}


class AiSettingsRequest(BaseModel):
    provider: str
    model: str


async def get_ai_config() -> dict:
    """Retorna config de IA atual (DB tem prioridade sobre .env)."""
    from config.settings import settings

    doc = await mongodb_client.database[COLLECTION].find_one({"_id": DOC_ID})
    if doc:
        return {"provider": doc["provider"], "model": doc["model"]}
    # fallback para .env
    provider = settings.ai_provider.lower()
    if provider == "anthropic":
        return {"provider": "anthropic", "model": settings.anthropic_model}
    return {"provider": "openai", "model": settings.openai_model}


@router.get("/ai")
async def get_ai_settings():
    config = await get_ai_config()
    return {**config, "available_models": MODELS}


@router.put("/ai")
async def update_ai_settings(body: AiSettingsRequest):
    await mongodb_client.database[COLLECTION].update_one(
        {"_id": DOC_ID},
        {"$set": {"provider": body.provider, "model": body.model}},
        upsert=True,
    )
    return {"provider": body.provider, "model": body.model}
