"""knowledge_units + unit_permissions.

Revision ID: 0003_knowledge
Revises: 0002_seed
Create Date: 2026-08-26
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0003_knowledge"
down_revision: Union[str, None] = "0002_seed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "knowledge_units",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("unit_code", sa.String(length=64), nullable=False, unique=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=64), nullable=True),
        sa.Column("tags", JSONB(), nullable=True),
        sa.Column("source_file_name", sa.String(length=255), nullable=True),
        sa.Column("file_type", sa.String(length=32), nullable=True),
        sa.Column("file_size", sa.BigInteger(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("creator_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_knowledge_units_unit_code", "knowledge_units", ["unit_code"])
    op.create_index("ix_knowledge_units_status", "knowledge_units", ["status"])
    op.create_index("ix_knowledge_units_category", "knowledge_units", ["category"])
    op.create_index("ix_knowledge_units_creator_id", "knowledge_units", ["creator_id"])

    op.create_table(
        "unit_permissions",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("unit_id", sa.BigInteger(), sa.ForeignKey("knowledge_units.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_type", sa.String(length=32), nullable=False),
        sa.Column("target_id", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("unit_id", "target_type", "target_id", name="uq_unit_perm_triplet"),
    )
    op.create_index("ix_unit_permissions_unit_id", "unit_permissions", ["unit_id"])


def downgrade() -> None:
    op.drop_table("unit_permissions")
    op.drop_table("knowledge_units")