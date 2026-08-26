"""Knowledge gap ORM — aggregated questions the KB did not answer well."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from admin.db.base import Base


class KnowledgeGap(Base):
    __tablename__ = "knowledge_gaps"
    __table_args__ = (
        Index("ix_knowledge_gaps_status", "status"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    question_pattern: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    sample_questions_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    ask_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    last_asked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="unresolved")
    resolved_unit_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("knowledge_units.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )