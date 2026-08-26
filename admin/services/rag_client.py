"""Async HTTP client for the RAG engine.

Centralises all admin → RAG calls so that:
- a single RAG_BASE_URL setting drives every endpoint;
- failures are mapped to ``RAGUnavailableError`` for the unified error envelope;
- headers (X-User-Id, X-Session-Id) are attached consistently.
"""
from __future__ import annotations

import logging
from typing import Any

import httpx

from admin.core.config import get_settings
from admin.core.exceptions import RAGUnavailableError

logger = logging.getLogger(__name__)

_TIMEOUT = httpx.Timeout(connect=1.5, read=30.0, write=30.0, pool=1.5)


def _client() -> httpx.AsyncClient:
    settings = get_settings()
    return httpx.AsyncClient(base_url=settings.RAG_BASE_URL, timeout=_TIMEOUT)


def _headers(*, user_id: int | None = None, session_id: str | None = None) -> dict[str, str]:
    h: dict[str, str] = {}
    if user_id is not None:
        h["X-User-Id"] = str(user_id)
    if session_id is not None:
        h["X-Session-Id"] = session_id
    return h


async def recall(
    query: str,
    *,
    top_k: int = 10,
    item_names: list[str] | None = None,
    user_id: int | None = None,
) -> list[dict[str, Any]]:
    """POST /api/v1/recall → list of {file_title, item_name, score}."""
    body = {"query": query, "top_k": top_k}
    if item_names:
        body["item_names"] = item_names
    try:
        async with _client() as c:
            r = await c.post("/api/v1/recall", json=body, headers=_headers(user_id=user_id))
    except httpx.HTTPError as e:
        raise RAGUnavailableError(f"RAG unreachable: {e}") from e
    if r.status_code >= 500:
        raise RAGUnavailableError(f"RAG recall failed: HTTP {r.status_code} {r.text[:200]}")
    r.raise_for_status()
    return r.json().get("hits", [])


async def embed(
    texts: list[str],
    *,
    user_id: int | None = None,
) -> dict[str, Any]:
    """POST /api/v1/embed → {dense, sparse}."""
    try:
        async with _client() as c:
            r = await c.post("/api/v1/embed", json={"texts": texts}, headers=_headers(user_id=user_id))
    except httpx.HTTPError as e:
        raise RAGUnavailableError(f"RAG unreachable: {e}") from e
    if r.status_code >= 500:
        raise RAGUnavailableError(f"RAG embed failed: HTTP {r.status_code} {r.text[:200]}")
    r.raise_for_status()
    return r.json()


async def upload_files(
    files: list[tuple[str, bytes, str]],
    *,
    user_id: int | None = None,
) -> dict[str, Any]:
    """POST /api/v1/upload — triggers RAG ingestion.

    ``files`` is a list of ``(filename, content_bytes, content_type)`` tuples.
    """
    multipart = [
        ("files", (name, content, ctype))
        for (name, content, ctype) in files
    ]
    try:
        async with _client() as c:
            r = await c.post(
                "/api/v1/upload",
                files=multipart,
                headers=_headers(user_id=user_id),
            )
    except httpx.HTTPError as e:
        raise RAGUnavailableError(f"RAG unreachable: {e}") from e
    if r.status_code >= 500:
        raise RAGUnavailableError(f"RAG upload failed: HTTP {r.status_code} {r.text[:200]}")
    r.raise_for_status()
    return r.json()