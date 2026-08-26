"""In-memory FAQ cache (LRU).

Phase 5 MVP: process-local dict with FIFO eviction. Phase 7 (settlement) will
seed this cache from ``faqs WHERE status='published'``. Semantic similarity
threshold is configurable via ``FAQ_MATCH_THRESHOLD`` (default 0.85).

Public API:
- ``put(question, answer, faq_id)`` — insert/replace
- ``exact_match(question)`` — punctuation/whitespace-normalized hit
- ``semantic_match(question_embedding)`` — cosine ≥ threshold
"""
from __future__ import annotations

import math
import re
import threading
from collections import OrderedDict

from admin.core.config import get_settings

_lock = threading.Lock()
_cache: "OrderedDict[str, dict]" = OrderedDict()
_MAX = 256

# Keep Chinese + ASCII letters + digits + spaces
_STRIP_RE = re.compile(r"[^\w一-鿿\s]+", re.UNICODE)
_SPACE_RE = re.compile(r"\s+")


def _settings_threshold() -> float:
    return float(get_settings().__dict__.get("FAQ_MATCH_THRESHOLD", 0.85))


def _normalize(question: str) -> str:
    s = _STRIP_RE.sub("", question.lower())
    s = _SPACE_RE.sub("", s).strip()
    return s


def put(question: str, answer: str, faq_id: int) -> None:
    key = _normalize(question)
    with _lock:
        if key in _cache:
            _cache.move_to_end(key)
        _cache[key] = {"answer": answer, "faq_id": faq_id, "embedding": None}
        if len(_cache) > _MAX:
            _cache.popitem(last=False)


def exact_match(question: str) -> dict | None:
    key = _normalize(question)
    with _lock:
        item = _cache.get(key)
    return item


def _cosine(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def semantic_match(question_embedding: list[float]) -> dict | None:
    """Returns the highest-scoring match above threshold, or None."""
    threshold = _settings_threshold()
    best: tuple[float, dict] | None = None
    with _lock:
        items = list(_cache.items())
    for key, val in items:
        emb = val.get("embedding")
        if not emb:
            continue
        score = _cosine(question_embedding, emb)
        if score >= threshold and (best is None or score > best[0]):
            best = (score, val)
    if best is None:
        return None
    return best[1]


def store_embedding(question: str, embedding: list[float]) -> None:
    """Attach an embedding to an existing cached entry (used by faq_miner)."""
    key = _normalize(question)
    with _lock:
        item = _cache.get(key)
        if item is not None:
            item["embedding"] = embedding


def size() -> int:
    with _lock:
        return len(_cache)


def clear() -> None:
    with _lock:
        _cache.clear()


__all__ = ["put", "exact_match", "semantic_match", "store_embedding", "size", "clear"]