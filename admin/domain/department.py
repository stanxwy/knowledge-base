"""Department ORM model — self-referencing tree."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from admin.db.base import Base

if TYPE_CHECKING:
    from admin.domain.user import User


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    parent_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    leader_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    parent: Mapped["Department | None"] = relationship("Department", remote_side="Department.id", backref="children")
    leader: Mapped["User | None"] = relationship("User", foreign_keys=[leader_id])