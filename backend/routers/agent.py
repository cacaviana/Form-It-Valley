from fastapi import APIRouter
from services.quote_generator import _get_model_name, _AGENT_INSTRUCTIONS, QuoteOutput

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.get("/info")
async def agent_info():
    """Retorna informacoes do agente IA (somente leitura)."""
    return {
        "model": await _get_model_name(),
        "instructions": _AGENT_INSTRUCTIONS,
        "output_schema": QuoteOutput.model_json_schema(),
    }
