"""Role + permission service."""
from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from admin.core import exceptions as exc
from admin.domain.permission import Permission, RolePermission
from admin.domain.role import Role
from admin.schemas.org import RoleCreate, RoleUpdate, RoleWithPermissions


async def list_roles(db: AsyncSession) -> list[RoleWithPermissions]:
    stmt = select(Role).order_by(Role.id.asc())
    roles = list((await db.execute(stmt)).scalars().all())
    out: list[RoleWithPermissions] = []
    for r in roles:
        codes = sorted({p.permission_code for p in r.permission_links})
        out.append(
            RoleWithPermissions(
                id=r.id,
                role_name=r.role_name,
                role_code=r.role_code,
                description=r.description,
                is_builtin=r.is_builtin,
                created_at=r.created_at,
                updated_at=r.updated_at,
                permissions=codes,
            )
        )
    return out


async def list_all_permissions(db: AsyncSession) -> list[Permission]:
    stmt = select(Permission).order_by(Permission.resource.asc(), Permission.action.asc())
    return list((await db.execute(stmt)).scalars().all())


async def get_role(db: AsyncSession, role_id: int) -> Role:
    role = (await db.execute(select(Role).where(Role.id == role_id))).scalar_one_or_none()
    if role is None:
        raise exc.NotFoundError(f"role {role_id} 不存在")
    return role


async def create_role(db: AsyncSession, payload: RoleCreate) -> Role:
    existing = (await db.execute(select(Role).where(Role.role_code == payload.role_code))).scalar_one_or_none()
    if existing is not None:
        raise exc.ConflictError(f"role_code '{payload.role_code}' 已存在")
    role = Role(
        role_name=payload.role_name,
        role_code=payload.role_code,
        description=payload.description,
        is_builtin=False,
    )
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


async def update_role(db: AsyncSession, role_id: int, payload: RoleUpdate) -> Role:
    role = await get_role(db, role_id)
    if role.is_builtin:
        # Allow editing name + description; never the code (FK risk).
        role.role_name = payload.role_name or role.role_name
        if payload.description is not None:
            role.description = payload.description
    else:
        data = payload.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(role, k, v)
    await db.commit()
    await db.refresh(role)
    return role


async def delete_role(db: AsyncSession, role_id: int) -> None:
    role = await get_role(db, role_id)
    if role.is_builtin:
        raise exc.ConflictError("内置角色不可删除")
    await db.delete(role)
    await db.commit()


async def replace_role_permissions(db: AsyncSession, role_id: int, codes: list[str]) -> Role:
    role = await get_role(db, role_id)
    # Wipe existing
    await db.execute(delete(RolePermission).where(RolePermission.role_id == role_id))
    # Insert fresh (de-duped)
    seen: set[str] = set()
    for raw in codes:
        code = raw.strip()
        if not code or code in seen:
            continue
        seen.add(code)
        perm_type = "action" if ":" in code else "menu"
        db.add(RolePermission(role_id=role_id, permission_code=code, permission_type=perm_type))
    await db.commit()
    await db.refresh(role)
    return role


async def get_role_permission_codes(db: AsyncSession, role_id: int) -> list[str]:
    role = await get_role(db, role_id)
    return sorted({p.permission_code for p in role.permission_links})