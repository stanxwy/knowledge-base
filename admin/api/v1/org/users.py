"""User router."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from admin.api.deps import require_permission
from admin.db.base import get_db
from admin.domain.user import User as UserModel
from admin.schemas.org import (
    PageResult,
    UserCreate,
    UserDetail,
    UserListQuery,
    UserOut,
    UserPasswordResetResponse,
    UserUpdate,
)
from admin.services import user_service

router = APIRouter(prefix="/api/org/users", tags=["org-users"])


@router.get("", response_model=PageResult)
async def list_users(
    q: UserListQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    _user: UserModel = Depends(require_permission("user:read")),
) -> PageResult:
    items, total = await user_service.list_users(db, q)
    return PageResult(items=[i.model_dump() for i in items], total=total, page=q.page, page_size=q.page_size)


@router.post("", response_model=UserDetail, status_code=201)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    _user: UserModel = Depends(require_permission("user:write")),
) -> UserDetail:
    return await user_service.create_user(db, payload)


@router.get("/{user_id}", response_model=UserDetail)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _user: UserModel = Depends(require_permission("user:read")),
) -> UserDetail:
    return await user_service.get_user_detail(db, user_id)


@router.put("/{user_id}", response_model=UserDetail)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _user: UserModel = Depends(require_permission("user:write")),
) -> UserDetail:
    return await user_service.update_user(db, user_id, payload)


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _user: UserModel = Depends(require_permission("user:write")),
) -> None:
    await user_service.delete_user(db, user_id)


@router.post("/{user_id}/reset-password", response_model=UserPasswordResetResponse)
async def reset_password(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _user: UserModel = Depends(require_permission("user:write")),
) -> UserPasswordResetResponse:
    new_pwd = await user_service.reset_password(db, user_id)
    return UserPasswordResetResponse(new_password=new_pwd)


@router.post("/{user_id}/toggle-status", response_model=UserOut)
async def toggle_status(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _user: UserModel = Depends(require_permission("user:write")),
) -> UserOut:
    user = await user_service.toggle_status(db, user_id)
    return UserOut.model_validate(user)