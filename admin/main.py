"""KBMS admin — FastAPI entrypoint.

Phase 1 scope: health probe + auth router (login/refresh/logout/me).
Phase 2+ will layer in org/knowledge/AI/dashboard/settlement routers and mount the
React SPA build at /admin/*.
"""
from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from admin.api.v1 import auth, health
from admin.api.v1.org import departments, roles, users
from admin.api.v1.knowledge import import_router, units as knowledge_units
from admin.api.v1.knowledge.import_router import rag_status_router
from admin.api.v1.ai import chat as ai_chat
from admin.api.v1.dashboard import stats as dashboard_stats
from admin.api.v1.settlement import faqs as settlement_faqs, gaps as settlement_gaps
from admin.core.config import get_settings
from admin.core.exceptions import KBMSError
from admin.core.logging import setup_logging
from admin.services import faq_miner

load_dotenv(override=True)
settings = get_settings()
setup_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Background task: refresh FAQ cache and run miner periodically.
    stop_event = asyncio.Event()

    async def _periodic_mine() -> None:
        from admin.db.base import AsyncSessionLocal
        interval = int(settings.__dict__.get("FAQ_MINER_INTERVAL_MIN", 60) or 60) * 60
        while not stop_event.is_set():
            try:
                async with AsyncSessionLocal() as db:
                    n_mined = await faq_miner.mine_candidates(db)
                    n_loaded = await faq_miner.refresh_published_cache(db)
                    if n_mined or n_loaded:
                        logger.info("FAQ background job: mined=%d, loaded=%d", n_mined, n_loaded)
            except Exception as e:  # pragma: no cover
                logger.exception("FAQ periodic mine crashed: %s", e)
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=interval)
            except asyncio.TimeoutError:
                continue

    task = asyncio.create_task(_periodic_mine())
    logger.info("KBMS admin started; FAQ miner scheduled every %s min", settings.__dict__.get("FAQ_MINER_INTERVAL_MIN", 60))
    try:
        yield
    finally:
        stop_event.set()
        task.cancel()
        try:
            await task
        except (asyncio.CancelledError, Exception):
            pass


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    # CORS — defaults stay permissive for local dev; tighten CORS_ALLOW_ORIGINS in .env.prod.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(KBMSError)
    async def kbms_error_handler(request: Request, exc: KBMSError) -> JSONResponse:
        body = {
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        }
        if exc.detail is not None:
            body["error"]["detail"] = exc.detail
        return JSONResponse(status_code=exc.status_code, content=body)

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(departments.router)
    app.include_router(roles.router)
    app.include_router(roles.permission_router)
    app.include_router(users.router)
    app.include_router(knowledge_units.router)
    app.include_router(import_router.router)
    app.include_router(rag_status_router)
    app.include_router(ai_chat.router)
    app.include_router(dashboard_stats.router)
    app.include_router(settlement_faqs.router)
    app.include_router(settlement_gaps.router)

    logger.info("%s v%s startup complete", settings.APP_NAME, settings.VERSION)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "admin.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
    )