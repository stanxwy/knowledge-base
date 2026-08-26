"""AI workbench router — chat SSE + session management."""
from __future__ import annotations

import asyncio
import json
import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from admin.api.deps import require_permission
from admin.core import exceptions as exc
from admin.db.base import AsyncSessionLocal, get_db
from admin.domain.user import User as UserModel
from admin.schemas.ai import ChatRequest, SessionSummary
from admin.services import ai_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["ai"])


def _sse_format(event: str, data: dict) -> bytes:
    """Format an SSE frame."""
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n".encode("utf-8")


@router.post("/chat/stream")
async def chat_stream(
    payload: ChatRequest,
    request: Request,
    user: UserModel = Depends(require_permission("ai:access")),
) -> StreamingResponse:
    """SSE-streaming chat endpoint — recall + check-permissions + RAG bridge."""
    # Use a background session so streaming can outlive the request body lifecycle.
    async def _gen():
        async with AsyncSessionLocal() as db:
            try:
                async for evt in ai_service.chat_stream(
                    db,
                    user=user,
                    question=payload.question,
                    session_id=payload.session_id,
                ):
                    if await request.is_disconnected():
                        break
                    yield _sse_format(evt["event"], evt["data"])
                    # tiny yield to event loop for client flush
                    await asyncio.sleep(0)
            except Exception as e:
                logger.exception("chat_stream crashed: %s", e)
                yield _sse_format("error", {"code": "internal_error", "message": str(e)})

    return StreamingResponse(
        _gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/sessions", response_model=list[SessionSummary])
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(require_permission("ai:access")),
) -> list[SessionSummary]:
    rows = await ai_service.list_sessions(db, user_id=user.id)
    return [
        SessionSummary(
            id=r.id,
            title=r.title,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in rows
    ]


@router.get("/sessions/{session_id}/messages")
async def session_messages(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(require_permission("ai:access")),
) -> dict:
    rows = await ai_service.list_session_messages(db, session_id=session_id)
    # Filter by ownership: only return rows belonging to current user.
    rows = [r for r in rows if r.user_id == user.id]
    return {
        "session_id": session_id,
        "items": [
            {
                "id": r.id,
                "role": "user" if r.id % 2 == 0 else "assistant",  # best-effort role
                "content": r.question if (r.id % 2 == 0) else r.answer,
                "source": r.source,
                "created_at": r.created_at,
            }
            for r in rows
        ],
    }


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(require_permission("ai:access")),
) -> None:
    ok = await ai_service.delete_session(db, user_id=user.id, session_id=session_id)
    if not ok:
        raise exc.NotFoundError(f"session {session_id} 不存在")