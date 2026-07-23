"""Login do Forms — proxy fino para a identidade central da Petra Suite.

O Forms nao autentica mais localmente: repassa email/senha para a plataforma
(PLATFORM_AUTH_URL) e devolve a resposta como esta (access_token, refresh_token,
user, tenant, products). O JWT emitido pela plataforma usa o mesmo
JWT_SECRET_KEY configurado aqui, entao require_access valida direto.
"""
import logging
import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
async def login(body: LoginRequest):
    """Autentica na plataforma Petra Suite e devolve a resposta (proxy fino)."""
    url = f"{settings.platform_auth_url.rstrip('/')}/api/auth/login"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                url,
                json={"email": body.email, "password": body.password},
            )
    except httpx.HTTPError as e:
        logger.error(f"Erro ao contatar a plataforma de identidade: {e}")
        raise HTTPException(
            status_code=502,
            detail="Servico de autenticacao indisponivel. Tente novamente.",
        )

    try:
        data = resp.json()
    except ValueError:
        logger.error(f"Resposta nao-JSON da plataforma (status {resp.status_code})")
        raise HTTPException(status_code=502, detail="Resposta invalida do servico de autenticacao")

    return JSONResponse(status_code=resp.status_code, content=data)
