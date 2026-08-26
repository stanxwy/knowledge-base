"""FastAPI dependencies — db session, current user, permission gates."""
from __future__ import annotations

import jwt
from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from admin.core import exceptions as exc
from admin.core.security import decode_token
from admin.db.base import get_db
from admin.domain.user import User
from admin.services import auth_service


async def get_current_user(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise exc.UnauthorizedError("缺少 Authorization Bearer token")
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_token(token, expected_type="access")
    except jwt.ExpiredSignatureError:
        raise exc.UnauthorizedError("access_token 已过期,请刷新")
    except jwt.PyJWTError as e:
        raise exc.UnauthorizedError(f"access_token 无效: {e}")

    user_id = int(payload["sub"])
    user = await auth_service.get_user_with_relations(db, user_id)
    if user.status != 1:
        raise exc.UnauthorizedError("账号已停用")
    return user


def require_permission(*codes: str):
    """FastAPI dependency factory: assert current user has at least one of ``codes``.

    Superusers bypass all permission checks.
    """
    async def _checker(user: User = Depends(get_current_user)) -> User:
        if user.is_superuser:
            return user
        held = {perm.permission_code for link in user.role_links for perm in link.role.permission_links}
        if not held.intersection(codes):
            raise exc.ForbiddenError(f"缺少权限: {', '.join(codes)}")
        return user

    return _checker


async def require_superuser(user: User = Depends(get_current_user)) -> User:
    if not user.is_superuser:
        raise exc.ForbiddenError("需要超级管理员权限")
    return user