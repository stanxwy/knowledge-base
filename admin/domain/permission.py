"""Permission dictionary + RolePermission (M:N binding)."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from admin.db.base import Base

if TYPE_CHECKING:
    from admin.domain.role import Role


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    permission_code: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    permission_type: Mapped[str] = mapped_column(String(32), nullable=False)
    resource: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class RolePermission(Base):
    """M:N binding between a role and a permission code.

    Stores the code as a string (not a FK to ``permissions.id``) so a role can
    bind to a code even before the permission is registered — handy for
    forward-compatibility and manual overrides.
    """

    __tablename__ = "role_permissions"
    __table_args__ = (UniqueConstraint("role_id", "permission_code", name="uq_role_perm_role_code"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    permission_code: Mapped[str] = mapped_column(String(128), nullable=False)
    permission_type: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    role: Mapped["Role"] = relationship("Role", back_populates="permission_links")