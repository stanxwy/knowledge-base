"""Auth router — login, refresh, logout, me."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from admin.api.deps import get_current_user
from admin.core.config import get_settings
from admin.db.base import get_db
from admin.domain.user import User
from admin.schemas.auth import (
    CurrentUserResponse,
    LoginRequest,
    LoginResponse,
    RefreshRequest,
)
from admin.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> LoginResponse:
    user = await auth_service.authenticate(db, payload.username, payload.password)
    await auth_service.record_login(db, user)
    access, refresh = auth_service.issue_tokens(user)
    permissions = auth_service.resolve_permissions(user)
    return LoginResponse(
        access_token=access,
        refresh_token=refresh,
        user_info=user,  # type: ignore[arg-type]
        permissions=permissions,
    )


@router.post("/refresh", response_model=LoginResponse)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)) -> LoginResponse:
    access, refresh, user = await auth_service.refresh_tokens(db, payload.refresh_token)
    permissions = auth_service.resolve_permissions(user)
    return LoginResponse(
        access_token=access,
        refresh_token=refresh,
        user_info=user,  # type: ignore[arg-type]
        permissions=permissions,
    )


@router.post("/logout")
async def logout() -> dict:
    """Client-side logout: server is stateless for tokens in this MVP.

    A Redis-backed token blacklist can be wired in later for instant revocation.
    """
    return {"detail": "logged out"}


@router.get("/me", response_model=CurrentUserResponse)
async def me(user: User = Depends(get_current_user)) -> CurrentUserResponse:
    role_codes = [link.role.role_code for link in user.role_links]
    permissions = auth_service.resolve_permissions(user)
    dept = None
    if user.department is not None:
        dept = {
            "id": user.department.id,
            "name": user.department.name,
            "parent_id": user.department.parent_id,
        }
    return CurrentUserResponse(
        user_info=user,  # type: ignore[arg-type]
        roles=role_codes,
        permissions=permissions,
        department=dept,
    )