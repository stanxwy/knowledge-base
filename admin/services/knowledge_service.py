"""Knowledge unit service — CRUD + import-anchor glue."""
from __future__ import annotations

from typing import Iterable

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from admin.core import exceptions as exc
from admin.domain.knowledge_unit import KnowledgeUnit
from admin.schemas.knowledge import (
    KnowledgeUnitCreate,
    KnowledgeUnitUpdate,
)
from admin.services.unit_code import generate_unit_code


async def _serialize_unit(u: KnowledgeUnit) -> dict:
    return {
        "id": u.id,
        "unit_code": u.unit_code,
        "title": u.title,
        "content": u.content,
        "summary": u.summary,
        "category": u.category,
        "tags": u.tags,
        "source_file_name": u.source_file_name,
        "file_type": u.file_type,
        "file_size": u.file_size,
        "status": u.status,
        "creator_id": u.creator_id,
        "created_at": u.created_at,
        "updated_at": u.updated_at,
        "permissions": [
            {
                "id": p.id,
                "target_type": p.target_type,
                "target_id": p.target_id,
                "created_at": p.created_at,
            }
            for p in u.permissions
        ],
    }


async def create_unit(db: AsyncSession, payload: KnowledgeUnitCreate, *, creator_id: int) -> dict:
    unit = KnowledgeUnit(
        unit_code=await generate_unit_code(db),
        title=payload.title,
        content=payload.content,
        summary=payload.summary,
        category=payload.category,
        tags=payload.tags,
        status=payload.status,
        creator_id=creator_id,
    )
    db.add(unit)
    await db.commit()
    await db.refresh(unit)
    # No permissions yet — default-deny
    return await _serialize_unit(unit)


async def _load_unit(db: AsyncSession, unit_id: int) -> KnowledgeUnit:
    stmt = select(KnowledgeUnit).where(KnowledgeUnit.id == unit_id)
    unit = (await db.execute(stmt)).scalar_one_or_none()
    if unit is None:
        raise exc.NotFoundError(f"knowledge unit {unit_id} 不存在")
    return unit


async def get_unit_detail(db: AsyncSession, unit_id: int) -> dict:
    unit = await _load_unit(db, unit_id)
    return await _serialize_unit(unit)


async def update_unit(db: AsyncSession, unit_id: int, payload: KnowledgeUnitUpdate) -> dict:
    unit = await _load_unit(db, unit_id)
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(unit, k, v)
    await db.commit()
    await db.refresh(unit)
    return await _serialize_unit(unit)


async def delete_units(db: AsyncSession, unit_ids: Iterable[int]) -> int:
    ids = list(unit_ids)
    if not ids:
        return 0
    stmt = select(KnowledgeUnit).where(KnowledgeUnit.id.in_(ids))
    units = list((await db.execute(stmt)).scalars().all())
    for u in units:
        await db.delete(u)
    await db.commit()
    return len(units)


async def list_units(
    db: AsyncSession,
    *,
    page: int,
    page_size: int,
    keyword: str | None = None,
    category: str | None = None,
    status: str | None = None,
    creator_id: int | None = None,
) -> tuple[list[dict], int]:
    stmt = select(KnowledgeUnit)
    if keyword:
        like = f"%{keyword.strip()}%"
        stmt = stmt.where(or_(KnowledgeUnit.title.ilike(like), KnowledgeUnit.unit_code.ilike(like)))
    if category:
        stmt = stmt.where(KnowledgeUnit.category == category)
    if status:
        stmt = stmt.where(KnowledgeUnit.status == status)
    if creator_id is not None:
        stmt = stmt.where(KnowledgeUnit.creator_id == creator_id)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()
    stmt = stmt.order_by(KnowledgeUnit.id.desc()).offset((page - 1) * page_size).limit(page_size)
    units = list((await db.execute(stmt)).scalars().unique().all())
    items = [await _serialize_unit(u) for u in units]
    return items, total