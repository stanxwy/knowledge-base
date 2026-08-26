"""Knowledge-module Pydantic schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, StringConstraints


TargetType = Literal["global", "department", "role", "user"]


# =========================
# Knowledge units
# =========================


class KnowledgeUnitBase(BaseModel):
    title: Annotated[str, StringConstraints(min_length=1, max_length=255)]
    content: Annotated[str, StringConstraints(min_length=1)]
    summary: str | None = None
    category: str | None = None
    tags: list[str] | None = None
    status: Literal["draft", "published", "archived"] = "draft"


class KnowledgeUnitCreate(KnowledgeUnitBase):
    pass


class KnowledgeUnitUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    summary: str | None = None
    category: str | None = None
    tags: list[str] | None = None
    status: Literal["draft", "published", "archived"] | None = None


class KnowledgeUnitOut(KnowledgeUnitBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    unit_code: str
    source_file_name: str | None = None
    file_type: str | None = None
    file_size: int | None = None
    creator_id: int
    created_at: datetime
    updated_at: datetime


class KnowledgeUnitDetail(KnowledgeUnitOut):
    """Knowledge unit with its configured data permissions."""
    permissions: list["UnitPermissionOut"] = []


class KnowledgeUnitListQuery(BaseModel):
    page: int = 1
    page_size: int = 20
    keyword: str | None = None
    category: str | None = None
    status: str | None = None
    creator_id: int | None = None


class BatchDeleteRequest(BaseModel):
    unit_ids: list[int]


# =========================
# Data permissions
# =========================


class UnitPermissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    target_type: TargetType
    target_id: int | None = None
    created_at: datetime


class UnitPermissionSpec(BaseModel):
    """One access rule on a knowledge unit."""
    target_type: TargetType
    target_id: int | None = None  # required unless target_type == 'global'


class UnitPermissionsReplace(BaseModel):
    """Replace the full permission set for a unit.

    The whole set is replaced atomically — no incremental diff.
    """
    permissions: list[UnitPermissionSpec]


class CheckPermissionsRequest(BaseModel):
    user_id: int
    unit_ids: list[int]


class CheckPermissionsResponse(BaseModel):
    authorized_unit_ids: list[int]
    unauthorized_unit_ids: list[int]


KnowledgeUnitDetail.model_rebuild()