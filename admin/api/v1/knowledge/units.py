"""Knowledge units router + data permission routers."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from admin.api.deps import require_permission
from admin.core import exceptions as exc
from admin.db.base import get_db
from admin.domain.user import User as UserModel
from admin.schemas.org import PageResult
from admin.schemas.knowledge import (
    BatchDeleteRequest,
    CheckPermissionsRequest,
    CheckPermissionsResponse,
    KnowledgeUnitCreate,
    KnowledgeUnitDetail,
    KnowledgeUnitUpdate,
    UnitPermissionsReplace,
)
from admin.services import data_permission_engine, knowledge_service

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.get("/units", response_model=PageResult)
async def list_units(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    keyword: str | None = None,
    category: str | None = None,
    status: str | None = None,
    creator_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    _user: UserModel = Depends(require_permission("knowledge:read")),
) -> PageResult:
    items, total = await knowledge_service.list_units(
        db,
        page=page,
        page_size=page_size,
        keyword=keyword,
        category=category,
        status=status,
        creator_id=creator_id,
    )
    return PageResult(items=items, total=total, page=page, page_size=page_size)


@router.post("/units", response_model=KnowledgeUnitDetail, status_code=201)
async def create_unit(
    payload: KnowledgeUnitCreate,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(require_permission("knowledge:write")),
) -> KnowledgeUnitDetail:
    raw = await knowledge_service.create_unit(db, payload, creator_id=user.id)
    return KnowledgeUnitDetail.model_validate(raw)


@router.get("/units/{unit_id}", response_model=KnowledgeUnitDetail)
async def get_unit(
    unit_id: int,
    db: AsyncSession = Depends(get_db),
    _user: UserModel = Depends(require_permission("knowledge:read")),
) -> KnowledgeUnitDetail:
    raw = await knowledge_service.get_unit_detail(db, unit_id)
    return KnowledgeUnitDetail.model_validate(raw)


@router.put("/units/{unit_id}", response_model=KnowledgeUnitDetail)
async def update_unit(
    unit_id: int,
    payload: KnowledgeUnitUpdate,
    db: AsyncSession = Depends(get_db),
    _user: UserModel = Depends(require_permission("knowledge:write")),
) -> KnowledgeUnitDetail:
    raw = await knowledge_service.update_unit(db, unit_id, payload)
    return KnowledgeUnitDetail.model_validate(raw)


@router.delete("/units", status_code=200)
async def batch_delete_units(
    payload: BatchDeleteRequest,
    db: AsyncSession = Depends(get_db),
    _user: UserModel = Depends(require_permission("knowledge:delete")),
) -> dict:
    deleted = await knowledge_service.delete_units(db, payload.unit_ids)
    return {"deleted": deleted}


# ===== Data permissions =====


@router.get("/units/{unit_id}/permissions", response_model=list[dict])
async def get_unit_permissions(
    unit_id: int,
    db: AsyncSession = Depends(get_db),
    _user: UserModel = Depends(require_permission("knowledge:read")),
) -> list[dict]:
    rows = await data_permission_engine.list_unit_permissions(db, unit_id)
    return [
        {"id": r.id, "target_type": r.target_type, "target_id": r.target_id, "created_at": r.created_at}
        for r in rows
    ]


@router.post("/units/{unit_id}/permissions", response_model=list[dict])
async def replace_unit_permissions(
    unit_id: int,
    payload: UnitPermissionsReplace,
    db: AsyncSession = Depends(get_db),
    _user: UserModel = Depends(require_permission("knowledge:write")),
) -> list[dict]:
    rows = await data_permission_engine.replace_unit_permissions(
        db,
        unit_id,
        [p.model_dump() for p in payload.permissions],
    )
    return [
        {"id": r.id, "target_type": r.target_type, "target_id": r.target_id, "created_at": r.created_at}
        for r in rows
    ]


@router.post("/check-permissions", response_model=CheckPermissionsResponse)
async def check_permissions(
    payload: CheckPermissionsRequest,
    db: AsyncSession = Depends(get_db),
    _user: UserModel = Depends(require_permission("knowledge:read")),
) -> CheckPermissionsResponse:
    if not payload.unit_ids:
        return CheckPermissionsResponse(authorized_unit_ids=[], unauthorized_unit_ids=[])
    result = await data_permission_engine.check_permissions(db, payload.user_id, payload.unit_ids)
    return CheckPermissionsResponse(**result)