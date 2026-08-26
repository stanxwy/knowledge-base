"""Knowledge import router — single/batch file upload + task polling."""
from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from admin.api.deps import require_permission
from admin.core import exceptions as exc
from admin.core.config import get_settings
from admin.db.base import get_db
from admin.domain.user import User as UserModel
from admin.schemas.import_task import ImportTaskStatus
from admin.services import import_task_store, importer

logger = logging.getLogger(__name__)

SUPPORTED_EXTS = {".pdf", ".docx", ".md", ".markdown", ".txt"}


def _ext_of(filename: str) -> str:
    from pathlib import Path

    return Path(filename).suffix.lower()


router = APIRouter(prefix="/api/knowledge", tags=["knowledge-import"])


async def _run_batch(
    *,
    task_id: str,
    files_payload: list[tuple[str, bytes]],
    creator_id: int,
    db_factory: Callable[[], Awaitable[AsyncSession]],
) -> None:
    """Run import in background with its own DB session."""
    db = await db_factory()
    try:
        await importer.import_batch(
            db,
            files=files_payload,
            creator_id=creator_id,
            task_id=task_id,
        )
    except Exception as e:
        logger.exception("Import batch %s crashed: %s", task_id, e)
        import_task_store.update_task(task_id, status="failed")
    finally:
        await db.close()


@router.post("/import", response_model=ImportTaskStatus, status_code=202)
async def import_files(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(require_permission("knowledge:import")),
) -> ImportTaskStatus:
    if not files:
        raise exc.ValidationError("至少上传一个文件")

    settings = get_settings()

    payload: list[tuple[str, bytes]] = []
    for f in files:
        content = await f.read()
        if not content:
            raise exc.ValidationError(f"文件 {f.filename} 为空")
        #  50 MB cap per SPEC §6.2
        if len(content) > 50 * 1024 * 1024:
            raise exc.ValidationError(f"文件 {f.filename} 超过 50MB 上限")
        ext = _ext_of(f.filename or "")
        if ext not in SUPPORTED_EXTS:
            raise exc.ValidationError(
                f"文件 {f.filename} 类型 {ext!r} 不支持(支持: {sorted(SUPPORTED_EXTS)})"
            )
        payload.append((f.filename or "unnamed", content))

    task = import_task_store.create_task([name for name, _ in payload])

    # Hand off to background with a fresh session.
    from admin.db.base import AsyncSessionLocal

    async def _session_factory() -> AsyncSession:
        return AsyncSessionLocal()

    background_tasks.add_task(
        _run_batch,
        task_id=task.task_id,
        files_payload=payload,
        creator_id=user.id,
        db_factory=_session_factory,
    )
    return task


@router.get("/tasks/{task_id}", response_model=ImportTaskStatus)
async def get_import_task(
    task_id: str,
    _user: UserModel = Depends(require_permission("knowledge:import")),
) -> ImportTaskStatus:
    task = import_task_store.get_task(task_id)
    if task is None:
        raise exc.NotFoundError(f"import task {task_id} 不存在或已过期(admin 重启后会清空)")
    return task