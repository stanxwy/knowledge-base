"""Liveness/readiness probe."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from admin.db.base import get_db

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)) -> dict:
    db_ok = True
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:  # pragma: no cover
        logger.warning("Health check DB ping failed: %s", e)
        db_ok = False
    return {
        "status": "ok" if db_ok else "degraded",
        "db": db_ok,
        "rag_reachable": None,  # populated in a later phase
    }