"""Knowledge-gap router — list, update status, one-click create-unit."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from admin.api.deps import require_permission
from admin.core import exceptions as exc
from admin.db.base import get_db
from admin.domain.user import User as UserModel
from admin.domain.knowledge_unit import KnowledgeUnit
from admin.schemas.settlement import (
    KnowledgeGapCreateUnitRequest,
    KnowledgeGapOut,
    KnowledgeGapUpdate,
)
from admin.services import gap_detector, knowledge_service

router = APIRouter(prefix="/api/settlement/knowledge-gaps", tags=["settlement-gaps"])


def _gap_to_out(row) -> KnowledgeGapOut:
    return KnowledgeGapOut(
        id=row.id,
        question_pattern=row.question_pattern,
        sample_questions=list(row.sample_questions_json or []),
        ask_count=row.ask_count,
        last_asked_at=row.last_asked_at,
        status=row.status,
        resolved_unit_id=row.resolved_unit_id,
        created_at=row.created_at,
    )


@router.get("", response_model=list[KnowledgeGapOut])
async def list_gaps(
    status: str | None = Query(default=None, description="unresolved|resolved|ignored"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _user: UserModel = Depends(require_permission("settlement:read")),
) -> list[KnowledgeGapOut]:
    rows, _total = await gap_detector.list_gaps(db, status=status, page=page, page_size=page_size)
    return [_gap_to_out(r) for r in rows]


@router.patch("/{gap_id}", response_model=KnowledgeGapOut)
async def update_gap(
    gap_id: int,
    payload: KnowledgeGapUpdate,
    db: AsyncSession = Depends(get_db),
    _user: UserModel = Depends(require_permission("settlement:write")),
) -> KnowledgeGapOut:
    row = await gap_detector.update_gap_status(db, gap_id, status=payload.status)
    if row is None:
        raise exc.NotFoundError(f"gap {gap_id} 不存在")
    return _gap_to_out(row)


@router.post("/{gap_id}/create-unit", response_model=KnowledgeGapOut)
async def create_unit_for_gap(
    gap_id: int,
    payload: KnowledgeGapCreateUnitRequest,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(require_permission("settlement:write")),
) -> KnowledgeGapOut:
    """Convert a gap into a draft knowledge unit and mark the gap resolved."""
    from admin.services.knowledge_service import _serialize_unit  # type: ignore
    from admin.schemas.knowledge import KnowledgeUnitCreate

    # Mark as resolved first so we can capture the new unit id.
    gap_row = (
        await gap_detector.update_gap_status(db, gap_id, status="resolved")
    )
    if gap_row is None:
        raise exc.NotFoundError(f"gap {gap_id} 不存在")

    unit_payload = KnowledgeUnitCreate(
        title=payload.title,
        content=payload.content,
        category=payload.category,
        status="draft",
    )
    raw = await knowledge_service.create_unit(db, unit_payload, creator_id=user.id)
    # Link gap → unit
    gap_row.resolved_unit_id = raw["id"]
    await db.commit()
    await db.refresh(gap_row)
    return _gap_to_out(gap_row)