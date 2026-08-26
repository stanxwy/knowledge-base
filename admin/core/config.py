"""Configuration for the KBMS admin service.

Mirrors the style of ``app/infra/config/settings.py``: a single
``Settings(BaseSettings)`` class read from ``.env`` and cached via
``get_settings()`` so tests can override via ``get_settings.cache_clear()``.
"""
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings as PydanticBaseSettings


# Resolve .env relative to this file so alembic / uvicorn invocations from
# different working directories all pick up the same config.
ADMIN_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = ADMIN_DIR / ".env"


class Settings(PydanticBaseSettings):
    APP_NAME: str = "KBMS Admin"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    APP_HOST: str = Field("0.0.0.0", env="APP_HOST")
    APP_PORT: int = Field(8002, env="APP_PORT")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")

    # ===== Postgres =====
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    DATABASE_SYNC_URL: str = Field(..., env="DATABASE_SYNC_URL")

    # ===== JWT =====
    JWT_SECRET: str = Field(..., env="JWT_SECRET")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    JWT_ACCESS_TTL_MIN: int = Field(30, env="JWT_ACCESS_TTL_MIN")
    JWT_REFRESH_TTL_DAY: int = Field(14, env="JWT_REFRESH_TTL_DAY")

    # ===== Bootstrap superuser =====
    INITIAL_SUPERUSER_USERNAME: str = Field("admin", env="INITIAL_SUPERUSER_USERNAME")
    INITIAL_SUPERUSER_PASSWORD: str = Field("admin123", env="INITIAL_SUPERUSER_PASSWORD")
    INITIAL_SUPERUSER_EMAIL: str = Field("admin@example.com", env="INITIAL_SUPERUSER_EMAIL")

    # ===== RAG engine integration =====
    RAG_BASE_URL: str = Field("http://localhost:8000", env="RAG_BASE_URL")

    # ===== CORS =====
    # Stored as a raw string to dodge pydantic-settings' default JSON-style
    # list parsing. ``cors_origins_list()`` splits it on demand.
    CORS_ALLOW_ORIGINS: str = Field(
        default="http://localhost:5173,http://localhost:8002",
        env="CORS_ALLOW_ORIGINS",
    )

    def cors_origins_list(self) -> list[str]:
        return [item.strip() for item in self.CORS_ALLOW_ORIGINS.split(",") if item.strip()]

    class Config:
        env_file = str(ENV_FILE)
        env_prefix = ""
        case_sensitive = True


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    if len(settings.JWT_SECRET) < 32:
        raise ValueError(
            "JWT_SECRET must be at least 32 characters long for production safety. "
            f"Got {len(settings.JWT_SECRET)} chars."
        )
    return settings