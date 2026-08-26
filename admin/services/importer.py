"""Document import service — parse + chunk + persist + dispatch to RAG.

Supported formats: PDF (via pypdf), DOCX (python-docx), Markdown, TXT.
Each parsed chunk becomes one KnowledgeUnit; the original ``unit_code`` is
injected as the RAG ``file_title`` so the two systems align on chunk recall.

Per SPEC §5.5, MVP uses **fixed-size chunking** (1500 chars). A later iteration
can plug in semantic / MinerU-based PDF parsing.
"""
from __future__ import annotations

import asyncio
import io
import logging
from pathlib import Path
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from admin.core import exceptions as exc
from admin.domain.knowledge_unit import KnowledgeUnit
from admin.services import knowledge_service, rag_client, import_task_store
from admin.services.unit_code import generate_unit_code

logger = logging.getLogger(__name__)

CHUNK_SIZE = 1500  # chars
SUPPORTED_EXTS = {".pdf", ".docx", ".md", ".txt", ".markdown"}

MIME_BY_EXT = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".md": "text/markdown",
    ".markdown": "text/markdown",
    ".txt": "text/plain",
}


# ---------- Parsing ---------- #


def _ext_of(filename: str) -> str:
    return Path(filename).suffix.lower()


def _parse_pdf(content: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as e:
        raise RuntimeError("pypdf 未安装") from e

    reader = PdfReader(io.BytesIO(content))
    parts: list[str] = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            parts.append("")
    return "\n".join(parts).strip()


def _parse_docx(content: bytes) -> str:
    try:
        from docx import Document
    except ImportError as e:
        raise RuntimeError("python-docx 未安装") from e

    doc = Document(io.BytesIO(content))
    return "\n".join(p.text for p in doc.paragraphs).strip()


def _parse_text(content: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "gbk", "gb18030", "latin-1"):
        try:
            return content.decode(encoding).strip()
        except UnicodeDecodeError:
            continue
    return content.decode("utf-8", errors="replace").strip()


def parse_document(filename: str, content: bytes) -> str:
    ext = _ext_of(filename)
    if ext not in SUPPORTED_EXTS:
        raise exc.ValidationError(f"不支持的文件类型: {ext} (支持: {sorted(SUPPORTED_EXTS)})")
    if ext == ".pdf":
        return _parse_pdf(content)
    if ext == ".docx":
        return _parse_docx(content)
    return _parse_text(content)


def chunk_text(text: str, size: int = CHUNK_SIZE) -> list[str]:
    """Split into ≤size chunks on paragraph boundaries when possible."""
    text = text.strip()
    if not text:
        return []
    if len(text) <= size:
        return [text]

    chunks: list[str] = []
    buf: list[str] = []
    buf_len = 0
    for paragraph in text.split("\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        # If single paragraph exceeds size, hard-split it.
        if len(paragraph) > size:
            if buf:
                chunks.append("\n".join(buf))
                buf, buf_len = [], 0
            for i in range(0, len(paragraph), size):
                chunks.append(paragraph[i : i + size])
            continue
        if buf_len + len(paragraph) + 1 > size and buf:
            chunks.append("\n".join(buf))
            buf, buf_len = [], 0
        buf.append(paragraph)
        buf_len += len(paragraph) + 1
    if buf:
        chunks.append("\n".join(buf))
    return chunks


def _title_from_chunk(filename: str, idx: int, chunk: str) -> str:
    """First non-empty line of the chunk (≤50 chars); falls back to filename + index."""
    for line in chunk.splitlines():
        line = line.strip().lstrip("#*- ").strip()
        if line:
            return line[:50]
    base = Path(filename).stem
    return f"{base} - 第{idx}段"


# ---------- Persistence + dispatch ---------- #


async def _create_unit_for_chunk(
    db: AsyncSession,
    *,
    creator_id: int,
    title: str,
    content: str,
    source_file_name: str,
    file_type: str,
    file_size: int,
) -> KnowledgeUnit:
    unit_code = await generate_unit_code(db)
    unit = KnowledgeUnit(
        unit_code=unit_code,
        title=title,
        content=content,
        source_file_name=source_file_name,
        file_type=file_type,
        file_size=file_size,
        status="draft",
        creator_id=creator_id,
    )
    db.add(unit)
    await db.flush()
    return unit


async def _upload_to_rag(*, user_id: int | None, filename: str, content: bytes, file_title: str) -> None:
    """Best-effort trigger of RAG ingestion. Errors are logged but do not fail
    the admin-side unit creation — admins can re-trigger ingestion later."""
    ext = _ext_of(filename)
    ctype = MIME_BY_EXT.get(ext, "application/octet-stream")
    try:
        await rag_client.upload_files(
            files=[(filename, content, ctype)],
            user_id=user_id,
        )
        logger.info("Dispatched RAG upload for file_title=%s", file_title)
    except Exception as e:
        logger.warning("RAG upload skipped for %s: %s", file_title, e)


async def import_one_file(
    db: AsyncSession,
    *,
    task_id: str,
    filename: str,
    content: bytes,
    creator_id: int,
) -> tuple[list[int], list[str]]:
    """Process a single file → returns (unit_ids, unit_codes).

    Failures raise but the caller marks the file as ``failed`` rather than
    aborting the whole batch.
    """
    ext = _ext_of(filename)
    if ext not in SUPPORTED_EXTS:
        raise exc.ValidationError(f"不支持的文件类型: {ext}")

    import_task_store.mark_file_status(task_id, filename, "parsing")
    text = parse_document(filename, content)
    chunks = chunk_text(text)
    if not chunks:
        raise RuntimeError("文档内容为空或解析失败")

    import_task_store.mark_file_status(task_id, filename, "ingesting")

    created_units: list[KnowledgeUnit] = []
    for idx, chunk in enumerate(chunks, start=1):
        title = _title_from_chunk(filename, idx, chunk)
        unit = await _create_unit_for_chunk(
            db,
            creator_id=creator_id,
            title=title,
            content=chunk,
            source_file_name=filename,
            file_type=ext.lstrip("."),
            file_size=len(content),
        )
        created_units.append(unit)

    await db.commit()
    # Refresh to populate unit_code (assigned by trigger) on each unit
    for u in created_units:
        await db.refresh(u)

    unit_ids = [u.id for u in created_units]
    unit_codes = [u.unit_code for u in created_units]

    # Dispatch each chunk to the RAG engine in parallel — using the chunk's
    # unit_code as the RAG ``file_title`` so recall can map back to admin units.
    async def _dispatch_one(unit: KnowledgeUnit) -> None:
        payload = f"# {unit.title}\n\n{unit.content}".encode("utf-8")
        await _upload_to_rag(
            user_id=creator_id,
            filename=f"{unit.unit_code}.md",
            content=payload,
            file_title=unit.unit_code,
        )

    await asyncio.gather(
        *[_dispatch_one(u) for u in created_units],
        return_exceptions=True,  # never let RAG errors fail the unit creation
    )

    return unit_ids, unit_codes


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
    for filename, content in files:
        try:
            unit_ids, unit_codes = await import_one_file(
                db,
                task_id=task_id,
                filename=filename,
                content=content,
                creator_id=creator_id,
            )
            import_task_store.record_file_done(
                task_id, filename, unit_codes=unit_codes, unit_ids=unit_ids
            )
        except Exception as e:
            any_failed = True
            logger.exception("Import failed for %s", filename)
            import_task_store.record_file_failed(task_id, filename, str(e))
            # Rollback the failed file's transaction
            await db.rollback()
    import_task_store.update_task(task_id, status="failed" if any_failed else "done")