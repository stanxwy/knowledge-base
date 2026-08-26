"""Dashboard router — metrics + rankings + daily trends."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from admin.api.deps import require_permission
from admin.core import exceptions as exc
from admin.db.base import get_db
from admin.domain.user import User as UserModel
from admin.schemas.dashboard import (
    DailyTrendPoint,
    DashboardMetrics,
    QuestionRank,
    UnitRank,
)
from admin.services import dashboard_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/metrics", response_model=DashboardMetrics)
async def metrics(
    range: str = Query("7d", description="today | 7d | 30d | all"),
    db: AsyncSession = Depends(get_db),
    _user: UserModel = Depends(require_permission("dashboard:read")),
) -> DashboardMetrics:
    return await dashboard_service.get_metrics(db, range_key=range)


@router.get("/rankings/questions", response_model=list[QuestionRank])
async def rank_questions(
    range: str = Query("7d"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    _user: UserModel = Depends(require_permission("dashboard:read")),
) -> list[QuestionRank]:
    if range not in {"today", "7d", "30d", "all"}:
        raise exc.ValidationError(f"不支持的时间范围: {range}")
    return await dashboard_service.rank_questions(db, range_key=range, limit=limit)


@router.get("/rankings/units", response_model=list[UnitRank])
async def rank_units(
    range: str = Query("7d"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    _user: UserModel = Depends(require_permission("dashboard:read")),
) -> list[UnitRank]:
    if range not in {"today", "7d", "30d", "all"}:
        raise exc.ValidationError(f"不支持的时间范围: {range}")
    return await dashboard_service.rank_units(db, range_key=range, limit=limit)


@router.get("/stats/tokens", response_model=list[DailyTrendPoint])
async def stats_tokens(
    range: str = Query("7d"),
    db: AsyncSession = Depends(get_db),
    _user: UserModel = Depends(require_permission("dashboard:read")),
) -> list[DailyTrendPoint]:
    if range not in {"today", "7d", "30d", "all"}:
        raise exc.ValidationError(f"不支持的时间范围: {range}")
    return await dashboard_service.daily_trends(db, range_key=range)