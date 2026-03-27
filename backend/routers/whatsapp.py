import httpx
from fastapi import APIRouter
from config.settings import settings

router = APIRouter(prefix="/api/whatsapp-templates", tags=["whatsapp"])


@router.get("")
async def list_templates():
    """Lista templates disponiveis no microsservico WhatsApp."""
    api_url = settings.whatsapp_api_url
    api_key = settings.whatsapp_api_key
    if not api_url or not api_key:
        return []

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(
                f"{api_url}/templates",
                headers={"X-API-Key": api_key},
            )
        if res.status_code == 200:
            return res.json()
        return []
    except Exception:
        return []
