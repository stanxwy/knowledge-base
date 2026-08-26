"""Domain ORM models — grouped into one module per aggregate.

Models inherit from ``admin.db.base.Base``. Importing this package triggers
SQLAlchemy metadata registration so Alembic autogenerate sees all tables.
"""
from admin.domain.user import User
from admin.domain.department import Department
from admin.domain.role import Role, UserRole
from admin.domain.permission import Permission, RolePermission
from admin.domain.knowledge_unit import KnowledgeUnit
from admin.domain.unit_permission import (
    UnitPermission,
    TARGET_GLOBAL,
    TARGET_DEPARTMENT,
    TARGET_ROLE,
    TARGET_USER,
    VALID_TARGET_TYPES,
)
from admin.domain.ai_session import AISession
from admin.domain.qa_access_log import QAAccessLog
from admin.domain.faq import FAQ
from admin.domain.knowledge_gap import KnowledgeGap

__all__ = [
    "User",
    "Department",
    "Role",
    "Permission",
    "UserRole",
    "RolePermission",
    "KnowledgeUnit",
    "UnitPermission",
    "TARGET_GLOBAL",
    "TARGET_DEPARTMENT",
    "TARGET_ROLE",
    "TARGET_USER",
    "VALID_TARGET_TYPES",
    "AISession",
    "QAAccessLog",
    "FAQ",
    "KnowledgeGap",
]