"""QA access log — one row per chat round; powers dashboard + FAQ mining + gap detection."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from admin.db.base import Base


class QAAccessLog(Base):
    __tablename__ = "qa_access_logs"
    __table_args__ = (
        Index("ix_qa_logs_user_id_created_at", "user_id", "created_at"),
        Index("ix_qa_logs_is_gap", "is_gap"),
        Index("ix_qa_logs_question_pattern", "question_pattern"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    question_pattern: Mapped[str | None] = mapped_column(String(255), nullable=True)
    answer: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    recalled_unit_ids_json: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    authorized_unit_ids_json: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    unauthorized_unit_ids_json: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    source: Mapped[str | None] = mapped_column(String(32), nullable=True)  # "faq" | "rag"
    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    completion_tokens: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    total_tokens: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    response_time_ms: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    is_gap: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )