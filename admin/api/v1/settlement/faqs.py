"""FAQ settlement router — recommendations, review, manual creation."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from admin.api.deps import require_permission
from admin.core import exceptions as exc
from admin.db.base import get_db
from admin.domain.faq import FAQ
from admin.domain.user import User as UserModel
from admin.schemas.settlement import (
    FAQManualCreate,
    FAQPublished,
    FAQRecommendation,
    FAQReviewRequest,
)
from admin.services import faq_cache, faq_miner

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/settlement/faqs", tags=["settlement-faqs"])


def _faq_to_recommendation(f: FAQ, ask_count: int = 0) -> FAQRecommendation:
    return FAQRecommendation(
        id=f.id,
        question=f.question,
        question_pattern=f.question_pattern,
        answer=f.answer,
        category=f.category,
        related_unit_id=f.related_unit_id,
        ask_count=ask_count,
        sample_questions=[],
        last_asked_at=None,
        created_at=f.created_at,
    )


def _faq_to_published(f: FAQ) -> FAQPublished:
    return FAQPublished(
        id=f.id,
        question=f.question,
        answer=f.answer,
        category=f.category,
        related_unit_id=f.related_unit_id,
        hit_count=f.hit_count,
        created_at=f.created_at,
        updated_at=f.updated_at,
    )


@router.get("/recommendations", response_model=list[FAQRecommendation])
async def list_recommendations(
    db: AsyncSession = Depends(get_db),
    _user: UserModel = Depends(require_permission("settlement:read")),
) -> list[FAQRecommendation]:
    """List auto-mined + manual pending_review FAQs."""
    from sqlalchemy import func
    rows = (
        await db.execute(
            select(FAQ, func.count().label("ask_count"))
            .where(FAQ.status == "pending_review")
            .outerjoin(  # left join via question_pattern; rough ask count
                # we don't have a direct FK; approximate via QA logs matching pattern
                __import__("admin").domain.qa_access_log.QAAccessLog,
                FAQ.question_pattern == __import__("admin").domain.qa_access_log.QAAccessLog.question_pattern,
            )
            .group_by(FAQ.id)
            .order_by(FAQ.created_at.desc())
        )
    ).all()
    return [_faq_to_recommendation(f, ask_count=int(c)) for f, c in rows]


@router.get("", response_model=list[FAQPublished])
async def list_published(
    db: AsyncSession = Depends(get_db),
    _user: UserModel = Depends(require_permission("settlement:read")),
) -> list[FAQPublished]:
    rows = (
        await db.execute(
            select(FAQ).where(FAQ.status == "published").order_by(FAQ.updated_at.desc())
        )
    ).scalars().all()
    return [_faq_to_published(f) for f in rows]


@router.post("", response_model=FAQPublished, status_code=201)
async def create_manual_faq(
    payload: FAQManualCreate,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(require_permission("settlement:write")),
) -> FAQPublished:
    """Manually create a FAQ. ``auto_publish=true`` publishes immediately."""
    faq = FAQ(
        question=payload.question,
        question_pattern=payload.question.lower().strip()[:255],
        answer=payload.answer,
        category=payload.category,
        related_unit_id=payload.related_unit_id,
        source_type="manual",
        status="published" if payload.auto_publish else "pending_review",
        reviewer_id=user.id if payload.auto_publish else None,
        reviewed_at=datetime.now(timezone.utc) if payload.auto_publish else None,
    )
    db.add(faq)
    await db.commit()
    await db.refresh(faq)
    if faq.status == "published":
        faq_cache.put(faq.question, faq.answer, faq.id)
    return _faq_to_published(faq)


@router.post("/{faq_id}/review", response_model=FAQPublished)
async def review_faq(
    faq_id: int,
    payload: FAQReviewRequest,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(require_permission("settlement:write")),
) -> FAQPublished:
    faq = (await db.execute(select(FAQ).where(FAQ.id == faq_id))).scalar_one_or_none()
    if faq is None:
        raise exc.NotFoundError(f"faq {faq_id} 不存在")
    if payload.edited_answer is not None:
        faq.answer = payload.edited_answer
    if payload.category is not None:
        faq.category = payload.category
    if payload.action == "approve":
        faq.status = "published"
        faq.reviewer_id = user.id
        faq.reviewed_at = datetime.now(timezone.utc)
        faq_cache.put(faq.question, faq.answer, faq.id)
    elif payload.action == "reject":
        faq.status = "rejected"
        faq.reviewer_id = user.id
        faq.reviewed_at = datetime.now(timezone.utc)
    else:
        raise exc.ValidationError(f"不支持的 review action: {payload.action}")
    await db.commit()
    await db.refresh(faq)
    return _faq_to_published(faq)


@router.post("/_run-mine", include_in_schema=False)
async def run_mine_now(
    db: AsyncSession = Depends(get_db),
    _user: UserModel = Depends(require_permission("settlement:write")),
) -> dict:
    """Operator-triggered FAQ miner (useful for tests / one-off runs)."""
    created = await faq_miner.mine_candidates(db)
    loaded = await faq_miner.refresh_published_cache(db)
    return {"mined": created, "loaded": loaded}