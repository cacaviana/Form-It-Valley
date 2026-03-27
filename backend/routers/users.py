from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from services.user_service import UserService

router = APIRouter(prefix="/api/users", tags=["users"])

_service = UserService()


class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    permissions: list[str] = []
    active: bool = True


class UpdateUserRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    permissions: Optional[list[str]] = None
    active: Optional[bool] = None


@router.get("")
async def list_users():
    """Lista todos os usuarios."""
    users = await _service.list_all()
    return {"users": users, "total": len(users)}


@router.get("/pages")
async def get_pages():
    """Retorna paginas disponiveis para permissao."""
    return _service.get_available_pages()


@router.get("/{user_id}")
async def get_user(user_id: str):
    """Busca usuario por ID."""
    user = await _service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    return user


@router.post("", status_code=201)
async def create_user(request: CreateUserRequest):
    """Cria novo usuario."""
    try:
        return await _service.create(request.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.put("/{user_id}")
async def update_user(user_id: str, request: UpdateUserRequest):
    """Atualiza usuario."""
    result = await _service.update(user_id, request.model_dump(exclude_none=True))
    if not result:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    return result


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: str):
    """Remove usuario."""
    deleted = await _service.delete(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
