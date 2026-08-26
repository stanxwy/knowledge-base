"""Seed built-in permissions and roles (super_admin, knowledge_admin, regular_user).

Revision ID: 0002_seed
Revises: 0001_init
Create Date: 2026-08-26
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002_seed"
down_revision: Union[str, None] = "0001_init"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_PERMISSIONS: list[tuple[str, str, str, str]] = [
    # (code, type, resource, action)
    ("org:read", "action", "org", "read"),
    ("org:write", "action", "org", "write"),
    ("user:read", "action", "user", "read"),
    ("user:write", "action", "user", "write"),
    ("role:read", "action", "role", "read"),
    ("role:write", "action", "role", "write"),
    ("knowledge:read", "action", "knowledge", "read"),
    ("knowledge:write", "action", "knowledge", "write"),
    ("knowledge:delete", "action", "knowledge", "delete"),
    ("knowledge:import", "action", "knowledge", "import"),
    ("ai:access", "action", "ai", "access"),
    ("dashboard:read", "action", "dashboard", "read"),
    ("settlement:read", "action", "settlement", "read"),
    ("settlement:write", "action", "settlement", "write"),
]


def upgrade() -> None:
    bind = op.get_bind()

    # ---- Seed permissions dictionary ----
    bind.execute(
        sa.text(
            "INSERT INTO permissions (permission_code, permission_type, resource, action, description) "
            "VALUES (:code, :type, :resource, :action, :description)"
        ),
        [
            {
                "code": code,
                "type": ptype,
                "resource": resource,
                "action": action,
                "description": f"{resource} {action}",
            }
            for code, ptype, resource, action in _PERMISSIONS
        ],
    )

    # ---- Seed built-in roles ----
    bind.execute(
        sa.text(
            "INSERT INTO roles (role_name, role_code, description, is_builtin) "
            "VALUES (:name, :code, :desc, true)"
        ),
        [
            {"name": "系统管理员", "code": "super_admin", "desc": "拥有全部操作权限"},
            {"name": "知识管理员", "code": "knowledge_admin", "desc": "负责知识维护、FAQ 审核、看板查看"},
            {"name": "普通用户", "code": "regular_user", "desc": "可访问 AI 对话与已授权知识"},
        ],
    )

    # ---- Bind role -> permissions ----
    rows = bind.execute(sa.text("SELECT id, role_code FROM roles")).fetchall()
    role_id_by_code = {row.role_code: row.id for row in rows}

    bindings: list[dict] = []
    for perm in _PERMISSIONS:
        code = perm[0]
        ptype = perm[1]
        if role_id_by_code.get("super_admin") is not None:
            bindings.append({"role_id": role_id_by_code["super_admin"], "code": code, "type": ptype})
        if code in {"knowledge:read", "knowledge:write", "knowledge:delete", "knowledge:import",
                    "ai:access", "dashboard:read", "settlement:read", "settlement:write", "org:read"}:
            if role_id_by_code.get("knowledge_admin") is not None:
                bindings.append({"role_id": role_id_by_code["knowledge_admin"], "code": code, "type": ptype})
        if code in {"knowledge:read", "ai:access"}:
            if role_id_by_code.get("regular_user") is not None:
                bindings.append({"role_id": role_id_by_code["regular_user"], "code": code, "type": ptype})

    bind.execute(
        sa.text(
            "INSERT INTO role_permissions (role_id, permission_code, permission_type) "
            "VALUES (:role_id, :code, :type)"
        ),
        bindings,
    )


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(sa.text("DELETE FROM role_permissions"))
    bind.execute(sa.text("DELETE FROM roles WHERE is_builtin = true"))
    bind.execute(sa.text("DELETE FROM permissions"))