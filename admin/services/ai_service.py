"""AI chat orchestrator.

Per SPEC §5.2 — the canonical flow:

  1. FAQ cache hit (exact / semantic) → emit `answer` + done, skip RAG.
  2. Recall: RAG ``/api/v1/recall`` returns list of {file_title, item_name, score}.
  3. Resolve each file_title → admin ``KnowledgeUnit.id`` via ``unit_code``.
  4. ``data_permission_engine.check_permissions(user_id, unit_ids)`` →
     authorized + unauthorized lists.
  5. If authorized is empty: emit `recall`/`unauthorized`/`done` with a friendly
     fallback answer and write a gap-marked ``QAAccessLog``.
  6. Else: POST RAG ``/api/v1/query`` (is_stream=true) carrying
     ``focus_file_titles`` = the authorized unit_codes; open RAG ``/stream/{sid}``;
     pipe each SSE event through to the client (``token`` → ``token``, ``done`` → ``done``).
  7. After RAG done: persist ``QAAccessLog`` row with recalled/authorized/unauthorized
     unit id lists, token counts (best-effort), and response time.
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from typing import AsyncIterator

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from admin.core import exceptions as exc
from admin.core.config import get_settings
from admin.domain.ai_session import AISession
from admin.domain.knowledge_unit import KnowledgeUnit
from admin.domain.qa_access_log import QAAccessLog
from admin.domain.user import User
from admin.services import data_permission_engine, faq_cache, rag_client

logger = logging.getLogger(__name__)


def _normalize_pattern(question: str) -> str:
    """Lowercase + collapse whitespace + strip trailing punctuation for grouping."""
    s = " ".join(question.lower().split())
    return s.strip(" ?!.,;:，。！？；：")[:255]


async def _resolve_unit_codes_to_ids(db: AsyncSession, unit_codes: list[str]) -> list[int]:
    if not unit_codes:
        return []
    stmt = select(KnowledgeUnit.id, KnowledgeUnit.unit_code).where(
        KnowledgeUnit.unit_code.in_(unit_codes)
    )
    rows = (await db.execute(stmt)).all()
    return [row[0] for row in rows]


async def _ensure_session(db: AsyncSession, user_id: int, session_id: str | None, title: str | None) -> AISession:
    if session_id and _is_valid_uuid(session_id):
        existing = (await db.execute(select(AISession).where(AISession.id == session_id))).scalar_one_or_none()
        if existing is not None and existing.user_id == user_id:
            if title and not existing.title:
                existing.title = title[:255]
            existing.updated_at = _now()
            await db.commit()
            return existing
    new_id = session_id if (session_id and _is_valid_uuid(session_id)) else uuid.uuid4().hex
    sess = AISession(id=new_id, user_id=user_id, title=(title[:255] if title else None))
    db.add(sess)
    await db.commit()
    return sess


def _now():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc)


async def _persist_access_log(
    db: AsyncSession,
    *,
    user_id: int,
    session_id: str,
    question: str,
    answer: str,
    recalled_unit_ids: list[int],
    authorized_unit_ids: list[int],
    unauthorized_unit_ids: list[int],
    source: str,
    response_time_ms: int,
    is_gap: bool,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
) -> None:
    log = QAAccessLog(
        session_id=session_id,
        user_id=user_id,
        question=question,
        question_pattern=_normalize_pattern(question),
        answer=answer[:60000],
        recalled_unit_ids_json=recalled_unit_ids,
        authorized_unit_ids_json=authorized_unit_ids,
        unauthorized_unit_ids_json=unauthorized_unit_ids,
        source=source,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
        response_time_ms=response_time_ms,
        is_gap=is_gap,
    )
    db.add(log)
    await db.commit()


async def chat_stream(
    db: AsyncSession,
    *,
    user: User,
    question: str,
    session_id: str | None,
) -> AsyncIterator[dict]:
    """Yield SSE-shaped dicts: ``{event, data}``.

    SSE 协议字段名见 SPEC §3.4:
      recall / authorized / unauthorized / token / done / error
    """
    settings = get_settings()
    started = time.monotonic()
    title_seed = question[:80]

    sess = await _ensure_session(db, user.id, session_id, title_seed)
    sid = sess.id

    # ===== Step 1: FAQ cache (exact) =====
    cached = faq_cache.exact_match(question)
    if cached is not None:
        answer = cached["answer"]
        yield {"event": "authorized", "data": {"unit_ids": [], "source": "faq"}}
        # emit the full answer as one token chunk so the client renders at once
        yield {"event": "token", "data": {"delta": answer}}
        elapsed_ms = int((time.monotonic() - started) * 1000)
        yield {
            "event": "done",
            "data": {
                "answer": answer,
                "source": "faq",
                "faq_id": cached.get("faq_id"),
                "session_id": sid,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "response_time_ms": elapsed_ms,
            },
        }
        await _persist_access_log(
            db,
            user_id=user.id,
            session_id=sid,
            question=question,
            answer=answer,
            recalled_unit_ids=[],
            authorized_unit_ids=[],
            unauthorized_unit_ids=[],
            source="faq",
            response_time_ms=elapsed_ms,
            is_gap=False,
        )
        return

    # ===== Step 2: recall =====
    try:
        hits = await rag_client.recall(question, top_k=10, user_id=user.id)
    except exc.RAGUnavailableError as e:
        yield {"event": "error", "data": {"message": str(e), "code": "rag_unavailable"}}
        return

    file_titles = [h["file_title"] for h in hits]
    recalled_unit_ids = await _resolve_unit_codes_to_ids(db, file_titles)

    yield {
        "event": "recall",
        "data": {
            "file_titles": file_titles,
            "unit_ids": recalled_unit_ids,
            "scores": [h.get("score") for h in hits],
        },
    }

    if not recalled_unit_ids:
        # No KB hits → treat as a gap; do not invoke RAG for a meaningless answer.
        elapsed_ms = int((time.monotonic() - started) * 1000)
        answer = "抱歉,知识库中暂无与该问题相关的内容。"
        yield {"event": "token", "data": {"delta": answer}}
        yield {
            "event": "done",
            "data": {
                "answer": answer,
                "source": "rag",
                "session_id": sid,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "response_time_ms": elapsed_ms,
            },
        }
        await _persist_access_log(
            db,
            user_id=user.id,
            session_id=sid,
            question=question,
            answer=answer,
            recalled_unit_ids=[],
            authorized_unit_ids=[],
            unauthorized_unit_ids=[],
            source="rag",
            response_time_ms=elapsed_ms,
            is_gap=True,
        )
        return

    # ===== Step 3: check permissions =====
    perm = await data_permission_engine.check_permissions(db, user.id, recalled_unit_ids)
    auth_ids: list[int] = perm["authorized_unit_ids"]
    unauth_ids: list[int] = perm["unauthorized_unit_ids"]

    yield {"event": "authorized", "data": {"unit_ids": auth_ids}}
    yield {"event": "unauthorized", "data": {"unit_ids": unauth_ids}}

    if not auth_ids:
        elapsed_ms = int((time.monotonic() - started) * 1000)
        answer = (
            "已从知识库中检索到相关条目,但您当前无权访问其内容。"
            "如需访问,请联系管理员调整数据权限。"
        )
        yield {"event": "token", "data": {"delta": answer}}
        yield {
            "event": "done",
            "data": {
                "answer": answer,
                "source": "rag",
                "session_id": sid,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "response_time_ms": elapsed_ms,
            },
        }
        await _persist_access_log(
            db,
            user_id=user.id,
            session_id=sid,
            question=question,
            answer=answer,
            recalled_unit_ids=recalled_unit_ids,
            authorized_unit_ids=auth_ids,
            unauthorized_unit_ids=unauth_ids,
            source="rag",
            response_time_ms=elapsed_ms,
            is_gap=True,
        )
        return

    # ===== Step 4: bridge to RAG /query + /stream =====
    auth_codes = (
        await db.execute(
            select(KnowledgeUnit.unit_code).where(KnowledgeUnit.id.in_(auth_ids))
        )
    ).scalars().all()
    auth_codes = list(auth_codes)

    rag_session_id = uuid.uuid4().hex  # RAG-side session for streaming
    try:
        async with httpx.AsyncClient(base_url=settings.RAG_BASE_URL, timeout=httpx.Timeout(connect=3.0, read=120.0, write=30.0, pool=3.0)) as client:
            submit = await client.post(
                "/api/v1/query",
                json={
                    "query": question,
                    "session_id": rag_session_id,
                    "is_stream": True,
                    "focus_file_titles": auth_codes,
                },
                headers={"X-User-Id": str(user.id), "X-Session-Id": sid},
            )
            submit.raise_for_status()
            async with client.stream(
                "GET",
                f"/api/v1/stream/{rag_session_id}",
                headers={"X-User-Id": str(user.id), "X-Session-Id": sid},
            ) as resp:
                async for raw_line in resp.aiter_lines():
                    if not raw_line:
                        continue
                    line = raw_line.strip()
                    if not line.startswith("data:"):
                        continue
                    payload = line[5:].strip()
                    if not payload:
                        continue
                    try:
                        evt = json.loads(payload)
                    except json.JSONDecodeError:
                        continue
                    # RAG SSE events:
                    #   {event: "progress" or "done" or "error", data: {...}}
                    evt_name = evt.get("event") or evt.get("type") or "message"
                    data = evt.get("data", evt)
                    if evt_name in ("progress", "PROGRESS"):
                        continue  # noisy; skip
                    if evt_name in ("done", "DONE"):
                        elapsed_ms = int((time.monotonic() - started) * 1000)
                        # Pull token counts if present
                        prompt_tokens = int(data.get("prompt_tokens", 0) or 0)
                        completion_tokens = int(data.get("completion_tokens", 0) or 0)
                        answer_text = data.get("answer") or data.get("text") or ""
                        yield {
                            "event": "done",
                            "data": {
                                "answer": answer_text,
                                "source": "rag",
                                "session_id": sid,
                                "prompt_tokens": prompt_tokens,
                                "completion_tokens": completion_tokens,
                                "response_time_ms": elapsed_ms,
                            },
                        }
                        await _persist_access_log(
                            db,
                            user_id=user.id,
                            session_id=sid,
                            question=question,
                            answer=answer_text,
                            recalled_unit_ids=recalled_unit_ids,
                            authorized_unit_ids=auth_ids,
                            unauthorized_unit_ids=unauth_ids,
                            source="rag",
                            response_time_ms=elapsed_ms,
                            is_gap=False,
                            prompt_tokens=prompt_tokens,
                            completion_tokens=completion_tokens,
                        )
                        return
                    if evt_name in ("error", "ERROR"):
                        yield {"event": "error", "data": data}
                        return
                    # Treat unknown events as token passthrough so the client
                    # at least sees *something*.
                    yield {"event": "token", "data": {"delta": str(data)}}
    except httpx.HTTPError as e:
        yield {"event": "error", "data": {"message": f"RAG stream error: {e}", "code": "rag_unavailable"}}


def _is_valid_uuid(value: str) -> bool:
    if not isinstance(value, str):
        return False
    try:
        uuid.UUID(value)
        return True
    except (ValueError, AttributeError):
        return False


async def list_sessions(db: AsyncSession, *, user_id: int, limit: int = 50) -> list[AISession]:
    stmt = select(AISession).where(AISession.user_id == user_id).order_by(AISession.updated_at.desc()).limit(limit)
    return list((await db.execute(stmt)).scalars().all())


async def delete_session(db: AsyncSession, *, user_id: int, session_id: str) -> bool:
    if not _is_valid_uuid(session_id):
        return False
    sess = (await db.execute(
        select(AISession).where(AISession.id == session_id, AISession.user_id == user_id)
    )).scalar_one_or_none()
    if sess is None:
        return False
    await db.delete(sess)
    await db.commit()
    return True


async def list_session_messages(db: AsyncSession, *, session_id: str, limit: int = 100) -> list[QAAccessLog]:
    if not _is_valid_uuid(session_id):
        return []
    stmt = (
        select(QAAccessLog)
        .where(QAAccessLog.session_id == session_id)
        .order_by(QAAccessLog.created_at.asc())
        .limit(limit)
    )
    return list((await db.execute(stmt)).scalars().all())