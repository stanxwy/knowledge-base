"""FAQ miner — periodically scan ``qa_access_logs`` and surface hot questions.

Per SPEC §5.3 / PRD §F-11:

- For each ``question_pattern`` whose ``count >= FAQ_MIN_FREQ_THRESHOLD``
  (default 5) in the last ``FAQ_MIN_WINDOW_DAYS`` (default 7) days:
    - skip if a FAQ with that pattern is already ``published``
    - skip if a pending-review FAQ exists for the same pattern
    - otherwise create a new FAQ with ``source_type=auto_mined`` and
      ``status=pending_review``, attaching the most-referenced
      ``KnowledgeUnit.id`` and the most-recent answer text (best effort).
- Also: refresh the in-memory FAQ cache from any published FAQ so the
  next chat round benefits from the cache immediately.

MVP uses the normalised ``question_pattern`` field as the dedup key
(semantic clustering belongs to a later iteration).
"""
from __future__ import annotations

import logging
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession

from admin.core.config import get_settings
from admin.domain.faq import FAQ
from admin.domain.qa_access_log import QAAccessLog

logger = logging.getLogger(__name__)


def _threshold() -> int:
    return int(get_settings().__dict__.get("FAQ_MIN_FREQ_THRESHOLD", 5) or 5)


def _window_days() -> int:
    return int(get_settings().__dict__.get("FAQ_MIN_WINDOW_DAYS", 7) or 7)


async def mine_candidates(db: AsyncSession) -> int:
    """Scan logs and create FAQ candidates.

    Returns the number of newly-created candidates.
    """
    threshold = _threshold()
    since = datetime.now(timezone.utc) - timedelta(days=_window_days())

    # Aggregate counts per question_pattern
    rows = (
        await db.execute(
            select(
                QAAccessLog.question_pattern,
                func_count().label("cnt"),
                func_max_ts().label("last_asked_at"),
            )
            .where(QAAccessLog.created_at >= since, QAAccessLog.question_pattern.isnot(None))
            .group_by(QAAccessLog.question_pattern)
            .having(func_count() >= threshold)
        )
    ).all()

    created = 0
    for pattern, cnt, last_asked_at in rows:
        # Skip if already covered by a published FAQ
        existing = (
            await db.execute(
                select(FAQ).where(
                    FAQ.question_pattern == pattern,
                    FAQ.status.in_(["published", "pending_review"]),
                )
            )
        ).scalar_one_or_none()
        if existing is not None:
            continue

        # Pull one sample question + most-referenced unit + most-recent answer
        sample = (
            await db.execute(
                select(QAAccessLog.question, QAAccessLog.answer, QAAccessLog.authorized_unit_ids_json)
                .where(QAAccessLog.question_pattern == pattern)
                .order_by(QAAccessLog.created_at.desc())
                .limit(10)
            )
        ).all()
        if not sample:
            continue

        # Most-referenced unit across the sample
        unit_counter: Counter[int] = Counter()
        for _q, _a, auth in sample:
            for uid in (auth or []):
                unit_counter[uid] += 1
        related_unit_id = unit_counter.most_common(1)[0][0] if unit_counter else None

        # Latest answer text as candidate answer
        latest_answer = (sample[0][1] or "").strip()[:2000]

        faq = FAQ(
            question=sample[0][0],
            question_pattern=pattern,
            answer=latest_answer or "(待补充)",
            source_type="auto_mined",
            status="pending_review",
        )
        if related_unit_id is not None:
            faq.related_unit_id = related_unit_id
        db.add(faq)
        created += 1

    if created:
        await db.commit()
        logger.info("FAQ miner created %d candidate(s)", created)
    return created


async def refresh_published_cache(db: AsyncSession) -> int:
    """Reload all ``published`` FAQs into the in-memory cache."""
    from admin.services import faq_cache

    rows = (
        await db.execute(select(FAQ).where(FAQ.status == "published"))
    ).scalars().all()
    for f in rows:
        faq_cache.put(f.question, f.answer, f.id)
    return len(rows)


# ---- tiny helpers to keep imports lean ----
from sqlalchemy import func as _sa_func  # noqa: E402


def func_count():  # noqa: D401
    return _sa_func.count()


def func_max_ts():  # noqa: D401
    return _sa_func.max(QAAccessLog.created_at)