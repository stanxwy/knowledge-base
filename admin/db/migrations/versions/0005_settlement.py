"""faqs + knowledge_gaps.

Revision ID: 0005_settlement
Revises: 0004_ai
Create Date: 2026-08-26
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005_settlement"
down_revision: Union[str, None] = "0004_ai"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "faqs",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("question_pattern", sa.String(length=255), nullable=True),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=True),
        sa.Column("related_unit_id", sa.BigInteger(), sa.ForeignKey("knowledge_units.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source_type", sa.String(length=32), nullable=False, server_default="manual"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending_review"),
        sa.Column("hit_count", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("reviewer_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_faqs_status", "faqs", ["status"])
    op.create_index("ix_faqs_question_pattern", "faqs", ["question_pattern"])
    op.create_index("ix_faqs_related_unit_id", "faqs", ["related_unit_id"])

    op.create_table(
        "knowledge_gaps",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("question_pattern", sa.String(length=255), nullable=False, unique=True),
        sa.Column("sample_questions_json", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("ask_count", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("last_asked_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="unresolved"),
        sa.Column("resolved_unit_id", sa.BigInteger(), sa.ForeignKey("knowledge_units.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_knowledge_gaps_status", "knowledge_gaps", ["status"])


def downgrade() -> None:
    op.drop_table("knowledge_gaps")
    op.drop_table("faqs")