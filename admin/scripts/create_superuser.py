"""Create the initial superuser from settings (idempotent).

Usage:
    python -m admin.scripts.create_superuser
    python -m admin.scripts.create_superuser --username foo --password bar --email foo@x.com

Reads defaults from settings.INITIAL_SUPERUSER_*. Safe to run multiple times —
existing user with the same username is updated (password reset + superuser flag).
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from admin.core.config import get_settings
from admin.core.logging import setup_logging
from admin.core.security import hash_password
from admin.db.base import AsyncSessionLocal
from admin.domain.role import Role, UserRole
from admin.domain.user import User

logger = logging.getLogger(__name__)


async def _ensure_superuser(
    db: AsyncSession,
    username: str,
    password: str,
    email: str | None,
    display_name: str | None = None,
) -> User:
    stmt = select(User).where(User.username == username)
    user = (await db.execute(stmt)).scalar_one_or_none()
    if user is None:
        user = User(
            username=username,
            password_hash=hash_password(password),
            display_name=display_name or username,
            email=email,
            is_superuser=True,
            status=1,
        )
        db.add(user)
        await db.flush()
        logger.info("Created initial superuser '%s' (id=%s)", username, user.id)
    else:
        user.password_hash = hash_password(password)
        user.is_superuser = True
        user.status = 1
        if email is not None:
            user.email = email
        logger.info("Reset superuser '%s' (id=%s)", username, user.id)

    # Bind super_admin role if present.
    role_stmt = select(Role).where(Role.role_code == "super_admin")
    role = (await db.execute(role_stmt)).scalar_one_or_none()
    if role is not None:
        link_stmt = select(UserRole).where(UserRole.user_id == user.id, UserRole.role_id == role.id)
        link = (await db.execute(link_stmt)).scalar_one_or_none()
        if link is None:
            db.add(UserRole(user_id=user.id, role_id=role.id))
            logger.info("Bound role 'super_admin' to user '%s'", username)

    await db.commit()
    return user


async def main_async(args: argparse.Namespace) -> None:
    settings = get_settings()
    username = args.username or settings.INITIAL_SUPERUSER_USERNAME
    password = args.password or settings.INITIAL_SUPERUSER_PASSWORD
    email = args.email or settings.INITIAL_SUPERUSER_EMAIL

    async with AsyncSessionLocal() as db:
        await _ensure_superuser(db, username, password, email, display_name=args.display_name)
    print(f"Superuser '{username}' is ready.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create/reset the initial superuser.")
    parser.add_argument("--username", help="override username (default from settings)")
    parser.add_argument("--password", help="override password (default from settings)")
    parser.add_argument("--email", help="override email")
    parser.add_argument("--display-name", help="display name shown in UI")
    args = parser.parse_args()

    setup_logging("INFO")
    try:
        asyncio.run(main_async(args))
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()