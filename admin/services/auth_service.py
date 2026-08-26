"""Auth service — login, refresh, current-user lookup, permission resolution."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from admin.core import exceptions as exc
from admin.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from admin.domain.user import User
from admin.domain.role import Role, UserRole
from admin.domain.permission import RolePermission

logger = logging.getLogger(__name__)


async def authenticate(db: AsyncSession, username: str, password: str) -> User:
    """Verify username/password. Raises ``UnauthorizedError`` on any failure."""
    stmt = (
        select(User)
        .options(selectinload(User.role_links).selectinload(UserRole.role).selectinload(Role.permission_links))
        .where(User.username == username)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None or not verify_password(password, user.password_hash):
        # Same message regardless of "user not found" vs "wrong password" — avoid leaking existence.
        raise exc.UnauthorizedError("用户名或密码错误")
    if user.status != 1:
        raise exc.UnauthorizedError("账号已停用,请联系管理员")
    return user


async def record_login(db: AsyncSession, user: User) -> None:
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()


def issue_tokens(user: User) -> tuple[str, str]:
    role_codes = [link.role.role_code for link in user.role_links]
    access = create_access_token(subject=user.id, extra_claims={"roles": role_codes})
    refresh = create_refresh_token(subject=user.id)
    return access, refresh


def resolve_permissions(user: User) -> list[str]:
    seen: set[str] = set()
    for link in user.role_links:
        for perm in link.role.permission_links:
            seen.add(perm.permission_code)
    return sorted(seen)


async def get_user_with_relations(db: AsyncSession, user_id: int) -> User:
    stmt = (
        select(User)
        .options(
            selectinload(User.department),
            selectinload(User.role_links).selectinload(UserRole.role).selectinload(Role.permission_links),
        )
        .where(User.id == user_id)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise exc.UnauthorizedError("用户不存在")
    return user


async def refresh_tokens(db: AsyncSession, refresh_token: str) -> tuple[str, str, User]:
    try:
        payload = decode_token(refresh_token, expected_type="refresh")
    except jwt.ExpiredSignatureError:
        raise exc.UnauthorizedError("refresh_token 已过期,请重新登录")
    except jwt.PyJWTError as e:
        raise exc.UnauthorizedError(f"refresh_token 无效: {e}")

    user_id = int(payload["sub"])
    user = await get_user_with_relations(db, user_id)
    if user.status != 1:
        raise exc.UnauthorizedError("账号已停用")
    access, refresh = issue_tokens(user)
    return access, refresh, user