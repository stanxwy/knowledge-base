"""KBMS admin — FastAPI entrypoint.

Phase 1 scope: health probe + auth router (login/refresh/logout/me).
Phase 2+ will layer in org/knowledge/AI/dashboard/settlement routers and mount the
React SPA build at /admin/*.
"""
from __future__ import annotations

import logging

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from admin.api.v1 import auth, health
from admin.api.v1.org import departments, roles, users
from admin.api.v1.knowledge import import_router, units as knowledge_units
from admin.api.v1.ai import chat as ai_chat
from admin.core.config import get_settings
from admin.core.exceptions import KBMSError
from admin.core.logging import setup_logging

load_dotenv(override=True)
settings = get_settings()
setup_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        debug=settings.DEBUG,
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
    app.include_router(ai_chat.router)

    @app.on_event("startup")
    async def on_startup() -> None:
        logger.info("%s v%s started on port %s", settings.APP_NAME, settings.VERSION, settings.APP_PORT)

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