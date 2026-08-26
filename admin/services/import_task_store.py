"""In-memory import task tracker (process-local).

Single-process MVP. Survives until the admin service restarts. Per SPEC §5.5,
MVP uses ``BackgroundTasks`` + an in-memory dict; later phases can swap in
Postgres-backed tasks without changing the public schema.
"""
from __future__ import annotations

import asyncio
import logging
import threading
import uuid
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

from admin.schemas.import_task import ImportTaskFileResult, ImportTaskStatus

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_tasks: dict[str, ImportTaskStatus] = {}
# Maps (admin_task_id, filename) → (unit_id, rag_task_id)
_rag_task_mapping: dict[tuple[str, str], tuple[int, str]] = {}
# Background polling tasks
_polling_tasks: dict[str, asyncio.Task[None]] = {}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _gen_task_id() -> str:
    return uuid.uuid4().hex


def create_task(file_names: list[str]) -> ImportTaskStatus:
    task_id = _gen_task_id()
    now = _now()
    task = ImportTaskStatus(
        task_id=task_id,
        status="pending",
        files=[ImportTaskFileResult(filename=f, status="pending") for f in file_names],
        created_at=now,
        updated_at=now,
    )
    with _lock:
        _tasks[task_id] = task
    return task


def get_task(task_id: str) -> ImportTaskStatus | None:
    return _tasks.get(task_id)


def update_task(
    task_id: str,
    *,
    status: str | None = None,
    mutate_files: Callable[[list[ImportTaskFileResult]], None] | None = None,
) -> None:
    with _lock:
        task = _tasks.get(task_id)
        if task is None:
            return
        if status is not None:
            task.status = status  # type: ignore[assignment]
        if mutate_files is not None:
            mutate_files(task.files)
        task.updated_at = _now()


def mark_file_status(task_id: str, filename: str, status: str) -> None:
    def _mutate(files: list[ImportTaskFileResult]) -> None:
        for f in files:
            if f.filename == filename:
                f.status = status  # type: ignore[assignment]
                return

    update_task(task_id, mutate_files=_mutate)


def record_file_done(
    task_id: str,
    filename: str,
    *,
    unit_codes: list[str] | None = None,
    unit_ids: list[int] | None = None,
    status: str = "done",
    message: str | None = None,
) -> None:
    def _mutate(files: list[ImportTaskFileResult]) -> None:
        for f in files:
            if f.filename == filename:
                f.status = status  # type: ignore[assignment]
                if unit_codes is not None:
                    f.unit_codes = unit_codes
                if unit_ids is not None:
                    f.unit_ids = unit_ids
                if message:
                    f.message = message
                return

    update_task(task_id, mutate_files=_mutate)


def record_file_failed(task_id: str, filename: str, error: str) -> None:
    def _mutate(files: list[ImportTaskFileResult]) -> None:
        for f in files:
            if f.filename == filename:
                f.status = "failed"
                f.error = error
                return

    update_task(task_id, mutate_files=_mutate)


# ---------- RAG task association ---------- #


def associate_rag_task(
    task_id: str,
    filename: str,
    unit_id: int,
    rag_task_id: str,
) -> None:
    """Associate an admin import task file with a RAG engine task."""
    with _lock:
        _rag_task_mapping[(task_id, filename)] = (unit_id, rag_task_id)


def get_rag_task_mapping(
    task_id: str, filename: str
) -> tuple[int, str] | None:
    """Get the (unit_id, rag_task_id) for a given admin task file."""
    return _rag_task_mapping.get((task_id, filename))


# ---------- Background polling ---------- #


def start_rag_polling(
    *,
    task_id: str,
    db_factory: Callable[[], Any],
    rag_tasks: dict[str, str],
    creator_id: int,
    poll_interval: int = 5,
) -> None:
    """Start background polling for RAG task completion.

    This is a fire-and-forget function that spawns an async task.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No event loop running (shouldn't happen in FastAPI)
        logger = logging.getLogger(__name__)
        logger.warning("Cannot start RAG polling: no event loop")
        return

    polling_task = loop.create_task(
        _poll_rag_tasks(
            task_id=task_id,
            db_factory=db_factory,
            rag_tasks=rag_tasks,
            creator_id=creator_id,
            poll_interval=poll_interval,
        )
    )
    with _lock:
        _polling_tasks[task_id] = polling_task


async def _poll_rag_tasks(
    *,
    task_id: str,
    db_factory: Callable[[], Any],
    rag_tasks: dict[str, str],
    creator_id: int,
    poll_interval: int,
) -> None:
    """Background coroutine to poll RAG task status and update KnowledgeUnits."""
    from admin.services import rag_client
    from admin.domain.knowledge_unit import KnowledgeUnit
    from sqlalchemy import update

    logger.info(f"[{task_id}] Starting RAG task polling for {len(rag_tasks)} files")

    max_retries = 60  # 5 minutes max
    retry_count = 0

    while retry_count < max_retries:
        await asyncio.sleep(poll_interval)
        retry_count += 1

        all_done = True
        db = None

        try:
            db = await db_factory()

            for filename, rag_task_id in rag_tasks.items():
                try:
                    status = await rag_client.get_task_status(rag_task_id)

                    if status == "completed":
                        # Update KnowledgeUnit status
                        mapping = get_rag_task_mapping(task_id, filename)
                        if mapping:
                            unit_id, _ = mapping
                            await db.execute(
                                update(KnowledgeUnit)
                                .where(KnowledgeUnit.id == unit_id)
                                .values(status="published")
                            )
                            await db.commit()
                            record_file_done(
                                task_id,
                                filename,
                                unit_ids=[unit_id],
                                unit_codes=[],
                                status="done",
                                message="RAG processing completed",
                            )
                            logger.info(f"[{task_id}] File {filename} processing completed")

                    elif status == "failed":
                        mapping = get_rag_task_mapping(task_id, filename)
                        if mapping:
                            unit_id, _ = mapping
                            await db.execute(
                                update(KnowledgeUnit)
                                .where(KnowledgeUnit.id == unit_id)
                                .values(status="failed")
                            )
                            await db.commit()
                        record_file_failed(
                            task_id,
                            filename,
                            "RAG processing failed",
                        )
                        logger.warning(f"[{task_id}] File {filename} processing failed")

                    else:
                        # Still processing
                        all_done = False

                except Exception as e:
                    logger.warning(
                        f"[{task_id}] Error polling RAG task {rag_task_id}: {e}"
                    )
                    all_done = False
        finally:
            if db:
                await db.close()

        if all_done:
            logger.info(f"[{task_id}] All RAG tasks completed")
            break

    if retry_count >= max_retries:
        logger.warning(f"[{task_id}] RAG polling timeout after {max_retries} retries")
        update_task(task_id, status="timeout")

    # Cleanup
    with _lock:
        _polling_tasks.pop(task_id, None)


__all__ = [
    "create_task",
    "get_task",
    "update_task",
    "mark_file_status",
    "record_file_done",
    "record_file_failed",
    "associate_rag_task",
    "get_rag_task_mapping",
    "start_rag_polling",
]
