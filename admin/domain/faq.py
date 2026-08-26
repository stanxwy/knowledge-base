"""FAQ ORM — auto-mined candidates + manually-curated entries.

Status flow: ``pending_review`` → (approve) → ``published`` | (reject) → ``rejected``.
``related_unit_id`` points to the most-referenced knowledge unit for context.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from admin.db.base import Base


class FAQ(Base):
    __tablename__ = "faqs"
    __table_args__ = (
        Index("ix_faqs_status", "status"),
        Index("ix_faqs_related_unit_id", "related_unit_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    question_pattern: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    related_unit_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("knowledge_units.id", ondelete="SET NULL"), nullable=True
    )
    source_type: Mapped[str] = mapped_column(String(32), nullable=False, default="manual")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending_review", index=True)
    hit_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    reviewer_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )