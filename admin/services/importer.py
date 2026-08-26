"""Document import service — upload raw files to RAG engine for processing.

This service now acts as a **thin metadata layer**:
1. Creates KnowledgeUnit records in Postgres (metadata only)
2. Uploads raw files to the RAG engine for full processing pipeline

The RAG engine (app/) handles:
- PDF/DOCX parsing via MinerU or pypdf
- Image extraction and processing
- Document chunking
- Vectorization and Milvus import

Per SPEC §5.5, admin tracks import tasks via ImportTaskStore and polls
the RAG engine for completion status.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from admin.core import exceptions as exc
from admin.db.base import AsyncSessionLocal
from admin.domain.knowledge_unit import KnowledgeUnit
from admin.services import knowledge_service, rag_client, import_task_store
from admin.services.unit_code import generate_unit_code

logger = logging.getLogger(__name__)

SUPPORTED_EXTS = {".pdf", ".docx", ".md", ".txt", ".markdown"}

MIME_BY_EXT = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".md": "text/markdown",
    ".markdown": "text/markdown",
    ".txt": "text/plain",
}


def _ext_of(filename: str) -> str:
    return Path(filename).suffix.lower()


# ---------- Persistence ---------- #


async def _create_unit_for_file(
    db: AsyncSession,
    *,
    creator_id: int,
    filename: str,
    content: str,
    file_size: int,
    file_type: str,
) -> KnowledgeUnit:
    """Create a single KnowledgeUnit for the raw file metadata.

    The content field stores the raw file content for now.
    After RAG processing completes, this can be updated with summary/metadata.
    """
    unit_code = await generate_unit_code(db)
    # Use filename stem as title (without extension)
    title = Path(filename).stem

    unit = KnowledgeUnit(
        unit_code=unit_code,
        title=title,
        content=content,  # Store raw content temporarily
        source_file_name=filename,
        file_type=file_type,
        file_size=file_size,
        status="pending",  # Will be updated to "processing" after RAG upload
        creator_id=creator_id,
    )
    db.add(unit)
    await db.flush()
    return unit


async def _upload_raw_file_to_rag(
    *,
    user_id: int | None,
    filename: str,
    content: bytes,
    unit_id: int,
) -> str | None:
    """Upload raw file to RAG engine for processing.

    Returns the RAG task_id if upload succeeds, None otherwise.
    """
    ext = _ext_of(filename)
    ctype = MIME_BY_EXT.get(ext, "application/octet-stream")
    try:
        result = await rag_client.upload_files(
            files=[(filename, content, ctype)],
            user_id=user_id,
        )
        # Extract task_id from RAG response
        rag_task_id = result.get("task_ids", [None])[0] if isinstance(result, dict) else None
        logger.info("Uploaded %s to RAG engine, unit_id=%s, rag_task_id=%s", filename, unit_id, rag_task_id)
        return rag_task_id
    except Exception as e:
        logger.warning("RAG upload failed for %s (unit_id=%s): %s", filename, unit_id, e)
        return None


async def import_one_file(
    db: AsyncSession,
    *,
    task_id: str,
    filename: str,
    content: bytes,
    creator_id: int,
) -> tuple[int, list[str]]:
    """Process a single file → returns (unit_id, rag_task_ids).

    Creates a single KnowledgeUnit for the file metadata, then uploads
    the raw file to the RAG engine for full processing.

    Failures raise but the caller marks the file as ``failed`` rather than
    aborting the whole batch.
    """
    ext = _ext_of(filename)
    if ext not in SUPPORTED_EXTS:
        raise exc.ValidationError(f"不支持的文件类型: {ext}")

    import_task_store.mark_file_status(task_id, filename, "parsing")

    # Decode content for storage (best effort)
    try:
        text_content = content.decode("utf-8")
    except UnicodeDecodeError:
        # For binary files (PDF, DOCX), store metadata note
        text_content = f"[Binary file: {filename}, size={len(content)} bytes]"

    # Create KnowledgeUnit with raw file metadata
    import_task_store.mark_file_status(task_id, filename, "ingesting")
    unit = await _create_unit_for_file(
        db,
        creator_id=creator_id,
        filename=filename,
        content=text_content,
        file_size=len(content),
        file_type=ext.lstrip("."),
    )

    await db.commit()
    await db.refresh(unit)

    # Upload to RAG engine
    rag_task_id = await _upload_raw_file_to_rag(
        user_id=creator_id,
        filename=filename,
        content=content,
        unit_id=unit.id,
    )

    # Update unit status
    if rag_task_id:
        unit.status = "processing"
        # Store the RAG task_id in a separate tracking mechanism
        # (will be used by polling logic)
        import_task_store.associate_rag_task(task_id, filename, unit.id, rag_task_id)
    else:
        unit.status = "failed"
        import_task_store.mark_file_status(task_id, filename, "failed")

    await db.commit()

    return unit.id, [rag_task_id] if rag_task_id else []


async def import_batch(
    db: AsyncSession,
    *,
    files: Iterable[tuple[str, bytes]],
    creator_id: int,
    task_id: str,
) -> None:
    """Process each file; mark each as done/failed; finalise task status."""
    import_task_store.update_task(task_id, status="running")
    any_failed = False

    # Track RAG task IDs for background polling
    rag_tasks: dict[str, str] = {}  # filename → rag_task_id

    for filename, content in files:
        try:
            unit_id, rag_task_ids = await import_one_file(
                db,
                task_id=task_id,
                filename=filename,
                content=content,
                creator_id=creator_id,
            )

            if rag_task_ids:
                rag_tasks[filename] = rag_task_ids[0]
                import_task_store.record_file_done(
                    task_id, filename, unit_ids=[unit_id], unit_codes=[],
                    status="uploaded", message="File uploaded to RAG engine, processing..."
                )
            else:
                import_task_store.record_file_failed(
                    task_id, filename, "Failed to upload to RAG engine"
                )
                any_failed = True

        except Exception as e:
            any_failed = True
            logger.exception("Import failed for %s", filename)
            import_task_store.record_file_failed(task_id, filename, str(e))
            await db.rollback()

    # Start background polling for RAG task status
    if rag_tasks:
        import_task_store.start_rag_polling(
            task_id=task_id,
            db_factory=AsyncSessionLocal,
            rag_tasks=rag_tasks,
            creator_id=creator_id,
        )

    import_task_store.update_task(task_id, status="done" if not any_failed else "failed")