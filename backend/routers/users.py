from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from services.user_service import UserService
from dependencies.tenant import TenantContext, get_tenant_context

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
async def list_users(ctx: TenantContext = Depends(get_tenant_context)):
    """Lista todos os usuarios do tenant."""
    users = await _service.list_all(tenant_id=ctx.tenant_id)
    return {"users": users, "total": len(users)}


@router.get("/pages")
async def get_pages():
    """Retorna paginas disponiveis para permissao."""
    return _service.get_available_pages()


@router.get("/{user_id}")
async def get_user(user_id: str, ctx: TenantContext = Depends(get_tenant_context)):
    """Busca usuario por ID (escopado ao tenant)."""
    user = await _service.get_by_id(user_id, tenant_id=ctx.tenant_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    return user


@router.post("", status_code=201)
async def create_user(request: CreateUserRequest, ctx: TenantContext = Depends(get_tenant_context)):
    """Cria novo usuario no tenant."""
    try:
        return await _service.create(request.model_dump(), tenant_id=ctx.tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.put("/{user_id}")
async def update_user(user_id: str, request: UpdateUserRequest, ctx: TenantContext = Depends(get_tenant_context)):
    """Atualiza usuario (escopado ao tenant)."""
    result = await _service.update(user_id, request.model_dump(exclude_none=True), tenant_id=ctx.tenant_id)
    if not result:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    return result


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: str, ctx: TenantContext = Depends(get_tenant_context)):
    """Remove usuario (escopado ao tenant)."""
    deleted = await _service.delete(user_id, tenant_id=ctx.tenant_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
