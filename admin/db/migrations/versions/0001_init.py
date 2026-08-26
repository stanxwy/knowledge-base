"""initial schema — users, departments, roles, permissions, user_roles, role_permissions

Revision ID: 0001_init
Revises:
Create Date: 2026-08-26
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_init"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "departments",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("parent_id", sa.BigInteger(), sa.ForeignKey("departments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("leader_id", sa.BigInteger(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_departments_parent_id", "departments", ["parent_id"])

    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(length=64), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=128), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True, unique=True),
        sa.Column("department_id", sa.BigInteger(), sa.ForeignKey("departments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_department_id", "users", ["department_id"])
    op.create_index("ix_users_status", "users", ["status"])

    # Add the FK from departments.leader_id -> users.id now that users exists.
    op.create_foreign_key(
        "fk_departments_leader_id_users",
        "departments",
        "users",
        ["leader_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "permissions",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("permission_code", sa.String(length=128), nullable=False, unique=True),
        sa.Column("permission_type", sa.String(length=32), nullable=False),
        sa.Column("resource", sa.String(length=64), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_permissions_permission_code", "permissions", ["permission_code"])

    op.create_table(
        "roles",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("role_name", sa.String(length=64), nullable=False),
        sa.Column("role_code", sa.String(length=64), nullable=False, unique=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("is_builtin", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_roles_role_code", "roles", ["role_code"])

    op.create_table(
        "user_roles",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role_id", sa.BigInteger(), sa.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "role_id", name="uq_user_roles_user_role"),
    )
    op.create_index("ix_user_roles_user_id", "user_roles", ["user_id"])
    op.create_index("ix_user_roles_role_id", "user_roles", ["role_id"])

    op.create_table(
        "role_permissions",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("role_id", sa.BigInteger(), sa.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("permission_code", sa.String(length=128), nullable=False),
        sa.Column("permission_type", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("role_id", "permission_code", name="uq_role_perm_role_code"),
    )
    op.create_index("ix_role_permissions_role_id", "role_permissions", ["role_id"])


def downgrade() -> None:
    op.drop_table("role_permissions")
    op.drop_table("user_roles")
    op.drop_table("roles")
    op.drop_table("permissions")
    op.drop_foreign_key("fk_departments_leader_id_users", "departments")
    op.drop_table("users")
    op.drop_table("departments")