"""Password hashing + JWT encode/decode + current user dependency helpers.

Style mirrors ``app/utils/`` — pure functions, no FastAPI dependency coupling.
FastAPI dependency wrappers live in ``admin.api.deps``.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

from admin.core.config import get_settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _pwd_context.verify(plain, hashed)
    except Exception:
        return False


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _create_token(
    payload: dict[str, Any],
    ttl: timedelta,
    *,
    secret: str,
    algorithm: str,
) -> str:
    data = {**payload, "iat": _now(), "exp": _now() + ttl, "jti": uuid.uuid4().hex}
    return jwt.encode(data, secret, algorithm=algorithm)


def create_access_token(*, subject: str | int, extra_claims: dict[str, Any] | None = None) -> str:
    settings = get_settings()
    payload: dict[str, Any] = {"sub": str(subject), "type": "access"}
    if extra_claims:
        payload.update(extra_claims)
    return _create_token(
        payload,
        timedelta(minutes=settings.JWT_ACCESS_TTL_MIN),
        secret=settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_refresh_token(*, subject: str | int) -> str:
    settings = get_settings()
    payload = {"sub": str(subject), "type": "refresh"}
    return _create_token(
        payload,
        timedelta(days=settings.JWT_REFRESH_TTL_DAY),
        secret=settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_token(token: str, *, expected_type: str | None = None) -> dict[str, Any]:
    """Decode a JWT and (optionally) verify its ``type`` claim.

    Raises ``jwt.PyJWTError`` subclasses on any failure; callers map to HTTP 401.
    """
    settings = get_settings()
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    if expected_type is not None and payload.get("type") != expected_type:
        raise jwt.InvalidTokenError(f"Expected token type '{expected_type}', got '{payload.get('type')}'")
    return payload