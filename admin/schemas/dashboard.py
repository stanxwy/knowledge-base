"""Dashboard Pydantic schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


# ===== Core metrics =====


class DashboardMetrics(BaseModel):
    total_visits: int
    unique_visitors: int
    total_knowledge_units: int
    total_tokens: int
    avg_response_time_ms: int
    range: str  # "today" | "7d" | "30d" | "all"


# ===== Rankings =====


class QuestionRank(BaseModel):
    question_pattern: str
    ask_count: int
    last_asked_at: datetime | None = None


class UnitRank(BaseModel):
    unit_id: int
    unit_code: str | None = None
    title: str
    mention_count: int


# ===== Trends (per-day series) =====


class DailyTrendPoint(BaseModel):
    date: str  # YYYY-MM-DD
    visits: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    avg_response_time_ms: int