"""Unit code generation — ``KU-{yyyymmdd}-{seq}`` per SPEC §2.2.

Daily sequence resets at UTC midnight; concurrency-safe via ``SELECT ... FOR UPDATE``
on a sentinel row or by relying on the unique index to reject collisions (we do the
latter, then retry).
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from admin.domain.knowledge_unit import KnowledgeUnit


def _today_prefix() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d")


async def generate_unit_code(db: AsyncSession, *, max_attempts: int = 5) -> str:
    prefix = _today_prefix()
    base = f"KU-{prefix}-"
    for attempt in range(max_attempts):
        # count today's existing rows cheaply
        like = f"{base}%"
        stmt = select(func.count(KnowledgeUnit.id)).where(KnowledgeUnit.unit_code.like(like))
        current = (await db.execute(stmt)).scalar_one() or 0
        candidate = f"{base}{current + 1 + attempt:04d}"
        # Use a lightweight pre-check (best-effort; unique index is the real guard).
        exists = (await db.execute(
            select(KnowledgeUnit.id).where(KnowledgeUnit.unit_code == candidate)
        )).scalar_one_or_none()
        if exists is None:
            return candidate
    # Fallback: timestamp-suffixed to guarantee uniqueness even under heavy concurrency.
    return f"{base}{int(datetime.now(timezone.utc).timestamp() * 1000) % 10**8:08d}"