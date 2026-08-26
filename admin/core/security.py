"""Password hashing + JWT encode/decode + current user dependency helpers.

Style mirrors ``app/utils/`` — pure functions, no FastAPI dependency coupling.
FastAPI dependency wrappers live in ``admin.api.deps``.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
import bcrypt

from admin.core.config import get_settings

# bcrypt 5.x enforces a 72-byte password limit and raises on overflow.
# Mirror the legacy silent truncation so hashing and verification stay consistent.
_BCRYPT_ROUNDS = 12
_BCRYPT_MAX_BYTES = 72


def _encode_password(plain: str) -> bytes:
    return plain.encode("utf-8")[:_BCRYPT_MAX_BYTES]


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(_encode_password(plain), bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_encode_password(plain), hashed.encode("utf-8"))
    except (ValueError, TypeError):
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