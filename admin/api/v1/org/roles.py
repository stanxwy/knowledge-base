"""Role + permission router."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from admin.api.deps import require_permission
from admin.db.base import get_db
from admin.domain.user import User
from admin.schemas.org import (
    PermissionOut,
    RoleCreate,
    RoleOut,
    RoleUpdate,
    RoleWithPermissions,
    RolePermissionsUpdate,
)
from admin.services import role_service

router = APIRouter(prefix="/api/org/roles", tags=["org-roles"])


@router.get("", response_model=list[RoleWithPermissions])
async def list_roles(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("role:read")),
) -> list[RoleWithPermissions]:
    return await role_service.list_roles(db)


@router.post("", response_model=RoleOut, status_code=201)
async def create_role(
    payload: RoleCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("role:write")),
) -> RoleOut:
    role = await role_service.create_role(db, payload)
    return RoleOut.model_validate(role)


@router.put("/{role_id}", response_model=RoleOut)
async def update_role(
    role_id: int,
    payload: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("role:write")),
) -> RoleOut:
    role = await role_service.update_role(db, role_id, payload)
    return RoleOut.model_validate(role)


@router.delete("/{role_id}", status_code=204)
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("role:write")),
) -> None:
    await role_service.delete_role(db, role_id)


@router.get("/{role_id}/permissions", response_model=list[str])
async def get_role_permissions(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("role:read")),
) -> list[str]:
    return await role_service.get_role_permission_codes(db, role_id)


@router.post("/{role_id}/permissions", response_model=RoleOut)
async def replace_role_permissions(
    role_id: int,
    payload: RolePermissionsUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("role:write")),
) -> RoleOut:
    role = await role_service.replace_role_permissions(db, role_id, payload.permission_codes)
    return RoleOut.model_validate(role)


# Top-level permission dictionary — exposed at /api/org/permissions
permission_router = APIRouter(prefix="/api/org/permissions", tags=["org-permissions"])


@permission_router.get("", response_model=list[PermissionOut])
async def list_permissions(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("role:read")),
) -> list[PermissionOut]:
    perms = await role_service.list_all_permissions(db)
    return [PermissionOut.model_validate(p) for p in perms]