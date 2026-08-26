"""Domain ORM models — grouped into one module per aggregate.

Models inherit from ``admin.db.base.Base``. Importing this package triggers
SQLAlchemy metadata registration so Alembic autogenerate sees all tables.
"""
from admin.domain.user import User
from admin.domain.department import Department
from admin.domain.role import Role, UserRole
from admin.domain.permission import Permission, RolePermission

__all__ = [
    "User",
    "Department",
    "Role",
    "Permission",
    "UserRole",
    "RolePermission",
]