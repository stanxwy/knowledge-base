"""In-memory import task tracker (process-local).

Single-process MVP. Survives until the admin service restarts. Per SPEC §5.5,
MVP uses ``BackgroundTasks`` + an in-memory dict; later phases can swap in
Postgres-backed tasks without changing the public schema.
"""
from __future__ import annotations

import threading
import uuid
from collections.abc import Callable
from datetime import datetime, timezone

from admin.schemas.import_task import ImportTaskFileResult, ImportTaskStatus

_lock = threading.Lock()
_tasks: dict[str, ImportTaskStatus] = {}


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
    unit_codes: list[str],
    unit_ids: list[int],
) -> None:
    def _mutate(files: list[ImportTaskFileResult]) -> None:
        for f in files:
            if f.filename == filename:
                f.status = "done"
                f.unit_codes = unit_codes
                f.unit_ids = unit_ids
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


__all__ = [
    "create_task",
    "get_task",
    "update_task",
    "mark_file_status",
    "record_file_done",
    "record_file_failed",
]