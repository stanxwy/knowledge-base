"""KnowledgeUnit ORM model — mirrors SPEC §2.2.

`unit_code` is the cross-system anchor that aligns with the RAG engine's
``file_title`` (admin → RAG via query param on upload).
"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from admin.db.base import Base

if TYPE_CHECKING:
    from admin.domain.user import User
    from admin.domain.unit_permission import UnitPermission


class KnowledgeUnit(Base):
    __tablename__ = "knowledge_units"
    __table_args__ = (
        Index("ix_knowledge_units_status", "status"),
        Index("ix_knowledge_units_category", "category"),
        Index("ix_knowledge_units_creator_id", "creator_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    unit_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    tags: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    source_file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    file_size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft", server_default="draft")
    creator_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    creator: Mapped["User"] = relationship("User", lazy="joined")
    permissions: Mapped[list["UnitPermission"]] = relationship(
        "UnitPermission",
        back_populates="unit",
        cascade="all, delete-orphan",
        lazy="selectin",
    )