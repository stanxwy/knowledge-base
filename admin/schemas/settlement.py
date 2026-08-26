"""Settlement (FAQ + knowledge-gap) Pydantic schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# ===== FAQs =====


class FAQRecommendation(BaseModel):
    """Auto-mined candidate awaiting human review."""
    id: int
    question: str
    question_pattern: str | None
    answer: str
    category: str | None = None
    related_unit_id: int | None = None
    ask_count: int
    sample_questions: list[str] = []
    last_asked_at: datetime | None = None
    created_at: datetime


class FAQPublished(BaseModel):
    id: int
    question: str
    answer: str
    category: str | None = None
    related_unit_id: int | None = None
    hit_count: int
    created_at: datetime
    updated_at: datetime


class FAQReviewRequest(BaseModel):
    action: Literal["approve", "reject"]
    edited_answer: str | None = None
    category: str | None = None


class FAQManualCreate(BaseModel):
    question: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)
    category: str | None = None
    related_unit_id: int | None = None
    auto_publish: bool = False


# ===== Knowledge Gaps =====


class KnowledgeGapOut(BaseModel):
    id: int
    question_pattern: str
    sample_questions: list[str]
    ask_count: int
    last_asked_at: datetime
    status: Literal["unresolved", "resolved", "ignored"]
    resolved_unit_id: int | None = None
    created_at: datetime


class KnowledgeGapUpdate(BaseModel):
    status: Literal["unresolved", "resolved", "ignored"]


class KnowledgeGapCreateUnitRequest(BaseModel):
    """One-click conversion of a knowledge gap into a draft knowledge unit."""
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    category: str | None = None