"""User service — CRUD + password reset + status toggle."""
from __future__ import annotations

import secrets
import string

from sqlalchemy import delete, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from admin.core import exceptions as exc
from admin.core.security import hash_password
from admin.domain.department import Department
from admin.domain.role import Role, UserRole
from admin.domain.user import User
from admin.schemas.org import (
    UserCreate,
    UserDetail,
    UserListQuery,
    UserUpdate,
)


async def _resolve_role_ids(db: AsyncSession, role_ids: list[int]) -> list[Role]:
    if not role_ids:
        return []
    stmt = select(Role).where(Role.id.in_(role_ids))
    roles = list((await db.execute(stmt)).scalars().all())
    found = {r.id for r in roles}
    missing = set(role_ids) - found
    if missing:
        raise exc.NotFoundError(f"role ids 不存在: {sorted(missing)}")
    return roles


async def create_user(db: AsyncSession, payload: UserCreate) -> UserDetail:
    # username uniqueness pre-check for friendlier 409
    existing = (await db.execute(select(User.id).where(User.username == payload.username))).scalar_one_or_none()
    if existing is not None:
        raise exc.ConflictError(f"用户名 '{payload.username}' 已存在")

    if payload.department_id is not None:
        exists = (await db.execute(select(Department.id).where(Department.id == payload.department_id))).scalar_one_or_none()
        if exists is None:
            raise exc.NotFoundError(f"department {payload.department_id} 不存在")

    roles = await _resolve_role_ids(db, payload.role_ids)

    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        display_name=payload.display_name,
        email=payload.email,
        department_id=payload.department_id,
        status=payload.status,
        is_superuser=False,
    )
    db.add(user)
    try:
        await db.flush()
    except IntegrityError as e:
        await db.rollback()
        raise exc.ConflictError(f"创建用户失败: {e.orig}") from e

    for r in roles:
        db.add(UserRole(user_id=user.id, role_id=r.id))
    await db.commit()
    return await get_user_detail(db, user.id)


async def update_user(db: AsyncSession, user_id: int, payload: UserUpdate) -> UserDetail:
    user = await _load_user(db, user_id)
    data = payload.model_dump(exclude_unset=True)

    if "role_ids" in data:
        new_role_ids = data.pop("role_ids") or []
        new_roles = await _resolve_role_ids(db, new_role_ids)
        await db.execute(delete(UserRole).where(UserRole.user_id == user_id))
        for r in new_roles:
            db.add(UserRole(user_id=user_id, role_id=r.id))

    if "department_id" in data and data["department_id"] is not None:
        exists = (await db.execute(select(Department.id).where(Department.id == data["department_id"]))).scalar_one_or_none()
        if exists is None:
            raise exc.NotFoundError(f"department {data['department_id']} 不存在")

    for k, v in data.items():
        if k == "role_ids":
            continue
        setattr(user, k, v)

    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        raise exc.ConflictError(f"更新用户失败: {e.orig}") from e
    await db.refresh(user)
    return await get_user_detail(db, user_id)


async def _load_user(db: AsyncSession, user_id: int) -> User:
    stmt = (
        select(User)
        .options(
            selectinload(User.department),
            selectinload(User.role_links).selectinload(UserRole.role),
        )
        .where(User.id == user_id)
    )
    user = (await db.execute(stmt)).scalar_one_or_none()
    if user is None:
        raise exc.NotFoundError(f"user {user_id} 不存在")
    return user


def _user_to_dict(u: User) -> dict:
    """Snapshot a User ORM object into a plain dict so pydantic does not trigger
    lazy loads when introspecting relationships like ``department`` /
    ``role_links`` after the session is closed or when attributes were not
    eager-loaded.
    """
    return {
        "id": u.id,
        "username": u.username,
        "display_name": u.display_name,
        "email": u.email,
        "department_id": u.department_id,
        "status": u.status,
        "is_superuser": u.is_superuser,
        "last_login_at": u.last_login_at,
        "created_at": u.created_at,
        "updated_at": u.updated_at,
    }


def _role_to_dict(r) -> dict:
    return {
        "id": r.id,
        "role_name": r.role_name,
        "role_code": r.role_code,
        "description": r.description,
        "is_builtin": r.is_builtin,
        "created_at": r.created_at,
        "updated_at": r.updated_at,
    }


def _dept_to_dict(d) -> dict | None:
    if d is None:
        return None
    return {
        "id": d.id,
        "name": d.name,
        "parent_id": d.parent_id,
        "leader_id": d.leader_id,
        "sort_order": d.sort_order,
        "created_at": d.created_at,
        "updated_at": d.updated_at,
    }


async def get_user_detail(db: AsyncSession, user_id: int) -> UserDetail:
    user = await _load_user(db, user_id)
    return UserDetail(
        **_user_to_dict(user),
        roles=[_role_to_dict(link.role) for link in user.role_links],
        department=_dept_to_dict(user.department),
    )


async def list_users(db: AsyncSession, q: UserListQuery) -> tuple[list[UserDetail], int]:
    stmt = select(User).options(
        selectinload(User.department),
        selectinload(User.role_links).selectinload(UserRole.role),
    )
    if q.keyword:
        like = f"%{q.keyword.strip()}%"
        stmt = stmt.where(or_(User.username.ilike(like), User.display_name.ilike(like)))
    if q.department_id is not None:
        stmt = stmt.where(User.department_id == q.department_id)
    if q.status is not None:
        stmt = stmt.where(User.status == q.status)
    if q.role_id is not None:
        stmt = stmt.join(UserRole, UserRole.user_id == User.id).where(UserRole.role_id == q.role_id)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()
    stmt = stmt.order_by(User.id.asc()).offset((q.page - 1) * q.page_size).limit(q.page_size)
    users = list((await db.execute(stmt)).scalars().unique().all())
    items = [
        UserDetail(
            **_user_to_dict(u),
            roles=[_role_to_dict(link.role) for link in u.role_links],
            department=_dept_to_dict(u.department),
        )
        for u in users
    ]
    return items, total


async def toggle_status(db: AsyncSession, user_id: int) -> User:
    user = await _load_user(db, user_id)
    if user.is_superuser:
        raise exc.ConflictError("超级管理员不可停用")
    user.status = 0 if user.status == 1 else 1
    await db.commit()
    await db.refresh(user)
    return user


def _generate_random_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


async def reset_password(db: AsyncSession, user_id: int) -> str:
    user = await _load_user(db, user_id)
    new_password = _generate_random_password()
    user.password_hash = hash_password(new_password)
    await db.commit()
    return new_password


async def delete_user(db: AsyncSession, user_id: int) -> None:
    user = await _load_user(db, user_id)
    if user.is_superuser:
        raise exc.ConflictError("超级管理员不可删除")
    await db.delete(user)
    await db.commit()


# --- local shims kept for backward compat (no longer used directly) --- #
from admin.schemas.org import DepartmentOut as DepartmentOut_safe  # noqa: E402  # noqa
from admin.schemas.org import RoleOut as RoleOut_safe  # noqa: E402  # noqa
from admin.schemas.org import UserOut as UserOut_safe  # noqa: E402  # noqa