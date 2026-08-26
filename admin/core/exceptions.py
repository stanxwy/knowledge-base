"""Business exception hierarchy.

All exceptions expose a ``code`` (machine-readable) and ``message`` (human-readable).
A single FastAPI exception handler converts them to the unified error envelope
defined in SPEC §3.8.
"""
from __future__ import annotations

from typing import Any


class KBMSError(Exception):
    status_code: int = 500
    code: str = "internal_error"

    def __init__(self, message: str, *, detail: Any = None) -> None:
        super().__init__(message)
        self.message = message
        self.detail = detail


class UnauthorizedError(KBMSError):
    status_code = 401
    code = "unauthorized"


class ForbiddenError(KBMSError):
    status_code = 403
    code = "forbidden"


class NotFoundError(KBMSError):
    status_code = 404
    code = "not_found"


class ConflictError(KBMSError):
    status_code = 409
    code = "conflict"


class ValidationError(KBMSError):
    status_code = 422
    code = "validation_error"


class RAGUnavailableError(KBMSError):
    status_code = 503
    code = "rag_unavailable"