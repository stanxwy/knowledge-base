"""AI workbench schemas (chat request, session, message)."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    session_id: str | None = None


class ChatMessage(BaseModel):
    id: int
    session_id: str
    role: str
    content: str
    source: str | None = None
    sources: list[dict] = []
    unauthorized_unit_ids: list[int] = []
    created_at: datetime


class SessionSummary(BaseModel):
    id: str
    title: str | None = None
    created_at: datetime
    updated_at: datetime