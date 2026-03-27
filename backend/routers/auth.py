import os
from fastapi import APIRouter, HTTPException, Response
from itvalleysecurity.fastapi import login_response
from pydantic import BaseModel
from services.user_service import UserService

router = APIRouter(prefix="/api/auth", tags=["auth"])

_user_service = UserService()

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@itvalley.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Itvalley01")


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
async def login(body: LoginRequest, response: Response):
    """Autentica usuario e retorna tokens JWT."""

    # 1. Super-admin (do .env) — acesso total
    if body.email == ADMIN_EMAIL and body.password == ADMIN_PASSWORD:
        tokens = login_response(response, sub=body.email, email=body.email, set_cookies=False)
        return {
            **tokens,
            "user": {
                "name": "Administrador",
                "email": ADMIN_EMAIL,
                "permissions": ["scheduling", "flows", "settings", "users"],
                "is_super_admin": True,
            }
        }

    # 2. Usuario cadastrado no MongoDB
    user = await _user_service.authenticate(body.email, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Email ou senha invalidos")

    tokens = login_response(response, sub=user["email"], email=user["email"], set_cookies=False)
    return {
        **tokens,
        "user": {
            "name": user["name"],
            "email": user["email"],
            "permissions": user["permissions"],
            "is_super_admin": False,
        }
    }
