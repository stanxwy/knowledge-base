"""Knowledge-gap detector — upsert gaps based on unresolved queries.

Triggered both at chat time (per round, when ``is_gap=True``) and on a
schedule (the periodic miner re-aggregates).

Status flow: ``unresolved`` → ``resolved`` (admin created a unit) /
``ignored`` (admin dismissed).
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from admin.domain.knowledge_gap import KnowledgeGap

logger = logging.getLogger(__name__)


async def upsert_gap(
    db: AsyncSession,
    *,
    question_pattern: str,
    sample_question: str,
) -> KnowledgeGap:
    """Insert or bump a gap row.

    Keeps the most recent sample question (cap at 10). Bumps ask_count.
    """
    if not question_pattern:
        return None  # type: ignore[return-value]
    row = (
        await db.execute(
            select(KnowledgeGap).where(KnowledgeGap.question_pattern == question_pattern)
        )
    ).scalar_one_or_none()

    now = datetime.now(timezone.utc)
    if row is None:
        row = KnowledgeGap(
            question_pattern=question_pattern,
            sample_questions_json=[sample_question[:500]],
            ask_count=1,
            last_asked_at=now,
            status="unresolved",
        )
        db.add(row)
        await db.commit()
        await db.refresh(row)
        return row

    row.ask_count = (row.ask_count or 0) + 1
    row.last_asked_at = now
    samples: list = list(row.sample_questions_json or [])
    if sample_question and sample_question not in samples:
        samples.append(sample_question[:500])
        if len(samples) > 10:
            samples = samples[-10:]
        row.sample_questions_json = samples
    if row.status in {"resolved", "ignored"}:
        # If new activity comes in, revert to unresolved so admins see it.
        row.status = "unresolved"
    await db.commit()
    await db.refresh(row)
    return row


async def list_gaps(
    db: AsyncSession,
    *,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[KnowledgeGap], int]:
    stmt = select(KnowledgeGap)
    if status is not None:
        stmt = stmt.where(KnowledgeGap.status == status)
    from sqlalchemy import func
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one()
    rows = (
        await db.execute(
            stmt.order_by(KnowledgeGap.ask_count.desc(), KnowledgeGap.last_asked_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    ).scalars().all()
    return list(rows), total


async def update_gap_status(
    db: AsyncSession,
    gap_id: int,
    *,
    status: str,
    resolved_unit_id: int | None = None,
) -> KnowledgeGap | None:
    row = (await db.execute(select(KnowledgeGap).where(KnowledgeGap.id == gap_id))).scalar_one_or_none()
    if row is None:
        return None
    row.status = status
    if resolved_unit_id is not None:
        row.resolved_unit_id = resolved_unit_id
    await db.commit()
    await db.refresh(row)
    return row


async def sync_from_logs(
    db: AsyncSession,
    *,
    patterns: Iterable[tuple[str, str]],
) -> int:
    """Bulk upsert gaps for an iterable of ``(pattern, sample)`` pairs.

    Used by APScheduler jobs that re-aggregate gap candidates.
    """
    count = 0
    for pattern, sample in patterns:
        if not pattern:
            continue
        await upsert_gap(db, question_pattern=pattern, sample_question=sample)
        count += 1
    return count