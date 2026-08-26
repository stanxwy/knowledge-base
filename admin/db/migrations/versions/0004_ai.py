"""ai_sessions + qa_access_logs.

Revision ID: 0004_ai
Revises: 0003_knowledge
Create Date: 2026-08-26
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004_ai"
down_revision: Union[str, None] = "0003_knowledge"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ai_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_ai_sessions_user_id", "ai_sessions", ["user_id"])

    op.create_table(
        "qa_access_logs",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("question_pattern", sa.String(length=255), nullable=True),
        sa.Column("answer", sa.Text(), nullable=False, server_default=""),
        sa.Column("recalled_unit_ids_json", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("authorized_unit_ids_json", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("unauthorized_unit_ids_json", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("source", sa.String(length=32), nullable=True),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completion_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("response_time_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_gap", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_qa_logs_user_id_created_at", "qa_access_logs", ["user_id", "created_at"])
    op.create_index("ix_qa_logs_session_id", "qa_access_logs", ["session_id"])
    op.create_index("ix_qa_logs_is_gap", "qa_access_logs", ["is_gap"])
    op.create_index("ix_qa_logs_question_pattern", "qa_access_logs", ["question_pattern"])


def downgrade() -> None:
    op.drop_table("qa_access_logs")
    op.drop_table("ai_sessions")