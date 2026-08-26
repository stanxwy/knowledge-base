"""Import-task related Pydantic schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class ImportTaskFileResult(BaseModel):
    filename: str
    status: Literal["pending", "parsing", "ingesting", "uploaded", "processing", "done", "failed", "timeout"]
    unit_codes: list[str] = []
    unit_ids: list[int] = []
    error: str | None = None
    message: str | None = None


class ImportTaskStatus(BaseModel):
    task_id: str
    status: Literal["pending", "running", "done", "failed", "timeout"]
    files: list[ImportTaskFileResult]
    created_at: datetime
    updated_at: datetime
