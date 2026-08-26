"""Role + UserRole (M:N) ORM models."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from admin.db.base import Base

if TYPE_CHECKING:
    from admin.domain.user import User
    from admin.domain.permission import RolePermission


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    role_name: Mapped[str] = mapped_column(String(64), nullable=False)
    role_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_builtin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    permission_links: Mapped[list["RolePermission"]] = relationship(
        "RolePermission",
        back_populates="role",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_roles_user_role"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="role_links")
    role: Mapped["Role"] = relationship("Role")