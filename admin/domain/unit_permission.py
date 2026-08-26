"""UnitPermission ORM — four-class (global/department/role/user) data access rules.

A unit with NO rows in this table grants access to nobody (default-deny,
per SPEC §5.1).
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from admin.db.base import Base

# Type constants — kept as module-level so services / routers import the same strings.
TARGET_GLOBAL = "global"
TARGET_DEPARTMENT = "department"
TARGET_ROLE = "role"
TARGET_USER = "user"
VALID_TARGET_TYPES = {TARGET_GLOBAL, TARGET_DEPARTMENT, TARGET_ROLE, TARGET_USER}


class UnitPermission(Base):
    __tablename__ = "unit_permissions"
    __table_args__ = (
        UniqueConstraint("unit_id", "target_type", "target_id", name="uq_unit_perm_triplet"),
        Index("ix_unit_permissions_unit_id", "unit_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    unit_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("knowledge_units.id", ondelete="CASCADE"), nullable=False
    )
    target_type: Mapped[str] = mapped_column(String(32), nullable=False)
    target_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    unit: Mapped["KnowledgeUnit"] = relationship("KnowledgeUnit", back_populates="permissions")  # noqa: F821