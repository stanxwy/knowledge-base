"""Dashboard analytics service — pure SQL aggregations over ``qa_access_logs``.

Per SPEC §5.7 / PRD §F-09 / §F-10 / §F-14:

- ``metrics`` — visits, UV, total tokens, avg response time, total knowledge units
- ``rankings/questions`` — top questions grouped by ``question_pattern`` (semantic
  dedup is approximated via the normalised pattern field for MVP — pure semantic
  clustering belongs to Phase 7 ``faq_miner``).
- ``rankings/units`` — most-mentioned knowledge units (aggregated over
  ``authorized_unit_ids_json``).
- ``stats/tokens`` — per-day series of tokens + response time + visit counts.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.asyncio import AsyncSession

from admin.core import exceptions as exc
from admin.domain.knowledge_unit import KnowledgeUnit
from admin.domain.qa_access_log import QAAccessLog
from admin.schemas.dashboard import (
    DailyTrendPoint,
    DashboardMetrics,
    QuestionRank,
    UnitRank,
)


_RANGE_DAYS = {
    "today": 1,
    "7d": 7,
    "30d": 30,
    "all": None,
}


def _range_start(range_key: str) -> datetime | None:
    days = _RANGE_DAYS.get(range_key)
    if days is None:
        return None
    return datetime.now(timezone.utc) - timedelta(days=days)


def _validate_range(range_key: str) -> str:
    if range_key not in _RANGE_DAYS:
        raise exc.ValidationError(f"不支持的时间范围: {range_key}")
    return range_key


# ============ Metrics ============


async def get_metrics(db: AsyncSession, *, range_key: str = "7d") -> DashboardMetrics:
    _validate_range(range_key)
    since = _range_start(range_key)

    base = select(QAAccessLog)
    if since is not None:
        base = base.where(QAAccessLog.created_at >= since)

    total_visits = (await db.execute(
        select(func.count()).select_from(base.subquery())
    )).scalar_one()
    unique_visitors = (await db.execute(
        select(func.count(func.distinct(QAAccessLog.user_id))).select_from(base.subquery())
    )).scalar_one()
    total_tokens = (await db.execute(
        select(func.coalesce(func.sum(QAAccessLog.total_tokens), 0)).select_from(base.subquery())
    )).scalar_one()
    avg_resp = (await db.execute(
        select(func.coalesce(func.avg(QAAccessLog.response_time_ms), 0)).select_from(base.subquery())
    )).scalar_one()

    total_kus = (await db.execute(
        select(func.count(KnowledgeUnit.id)).where(KnowledgeUnit.status != "archived")
    )).scalar_one()

    return DashboardMetrics(
        total_visits=total_visits,
        unique_visitors=unique_visitors,
        total_knowledge_units=total_kus,
        total_tokens=int(total_tokens),
        avg_response_time_ms=int(avg_resp),
        range=range_key,
    )


# ============ Rankings ============


async def rank_questions(
    db: AsyncSession,
    *,
    range_key: str = "7d",
    limit: int = 10,
) -> list[QuestionRank]:
    _validate_range(range_key)
    since = _range_start(range_key)

    base = select(QAAccessLog.question_pattern, func.count().label("ask_count"), func.max(QAAccessLog.created_at).label("last_asked_at"))
    base = base.where(QAAccessLog.question_pattern.isnot(None))
    if since is not None:
        base = base.where(QAAccessLog.created_at >= since)
    base = base.group_by(QAAccessLog.question_pattern).order_by(func.count().desc()).limit(limit)

    rows = (await db.execute(base)).all()
    return [
        QuestionRank(
            question_pattern=row[0],
            ask_count=int(row[1]),
            last_asked_at=row[2],
        )
        for row in rows
    ]


async def rank_units(
    db: AsyncSession,
    *,
    range_key: str = "7d",
    limit: int = 10,
) -> list[UnitRank]:
    """Top-K units by frequency in ``authorized_unit_ids_json``.

    Unnest each row's JSON array with ``jsonb_array_elements_text`` and group by
    unit_id. Range filter is applied before unnesting.
    """
    _validate_range(range_key)
    since = _range_start(range_key)

    uid_expr = func.cast(func.jsonb_array_elements_text(QAAccessLog.authorized_unit_ids_json), Integer)
    stmt = (
        select(
            uid_expr.label("uid"),
            func.count().label("mention_count"),
        )
        .where(QAAccessLog.authorized_unit_ids_json != sa.text("'[]'::jsonb"))
    )
    if since is not None:
        stmt = stmt.where(QAAccessLog.created_at >= since)
    rows = (await db.execute(stmt.group_by(uid_expr).order_by(func.count().desc()).limit(limit))).all()

    if not rows:
        return []

    ids = [int(r[0]) for r in rows if r[0] is not None]
    unit_meta = {
        u.id: (u.unit_code, u.title)
        for u in (await db.execute(
            select(KnowledgeUnit).where(KnowledgeUnit.id.in_(ids))
        )).scalars().all()
    }
    out: list[UnitRank] = []
    for r in rows:
        uid = int(r[0]) if r[0] is not None else None
        if uid is None:
            continue
        meta = unit_meta.get(uid)
        out.append(
            UnitRank(
                unit_id=uid,
                unit_code=meta[0] if meta else None,
                title=meta[1] if meta else f"unit#{uid}",
                mention_count=int(r[1]),
            )
        )
    return out


# Counter is used by FAQ miner (Phase 7) — keep the import here to avoid churn.
_ = Counter


# ============ Trends ============


async def daily_trends(
    db: AsyncSession,
    *,
    range_key: str = "7d",
) -> list[DailyTrendPoint]:
    _validate_range(range_key)
    days = _RANGE_DAYS[range_key]
    if days is None:
        # "all" — pick the last 30 days to avoid unbounded scans.
        days = 30
    since = datetime.now(timezone.utc) - timedelta(days=days)

    # date_trunc('day', created_at) returns a timestamp; cast to date for grouping.
    day_expr = func.cast(func.date_trunc("day", QAAccessLog.created_at), _DATE)
    stmt = (
        select(
            day_expr.label("day"),
            func.count().label("visits"),
            func.coalesce(func.sum(QAAccessLog.prompt_tokens), 0).label("prompt_tokens"),
            func.coalesce(func.sum(QAAccessLog.completion_tokens), 0).label("completion_tokens"),
            func.coalesce(func.sum(QAAccessLog.total_tokens), 0).label("total_tokens"),
            func.coalesce(func.avg(QAAccessLog.response_time_ms), 0).label("avg_resp"),
        )
        .where(QAAccessLog.created_at >= since)
        .group_by(day_expr)
        .order_by(day_expr.asc())
    )
    rows = (await db.execute(stmt)).all()

    # Fill missing days with zeros so the chart has a contiguous series.
    by_day: dict[str, list[float]] = {}
    for r in rows:
        d = r[0].isoformat() if hasattr(r[0], "isoformat") else str(r[0])[:10]
        by_day[d] = [int(r[1]), int(r[2]), int(r[3]), int(r[4]), int(r[5])]

    points: list[DailyTrendPoint] = []
    for i in range(days):
        d = (datetime.now(timezone.utc).date() - timedelta(days=days - 1 - i)).isoformat()
        vals = by_day.get(d, [0, 0, 0, 0, 0])
        points.append(
            DailyTrendPoint(
                date=d,
                visits=vals[0],
                prompt_tokens=vals[1],
                completion_tokens=vals[2],
                total_tokens=vals[3],
                avg_response_time_ms=vals[4],
            )
        )
    return points


# Use SQLAlchemy's Date type for the cast inside daily_trends.
from sqlalchemy import Date as _Date, Integer, sql as sa  # noqa: E402
_DATE = _Date