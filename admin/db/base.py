"""SQLAlchemy declarative base + async engine + session factory.

The single ``get_db`` dependency yields an ``AsyncSession`` and ensures proper
cleanup. Domain models inherit from ``Base`` and declare their tables here.
"""
from __future__ import annotations

from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from admin.core.config import get_settings

_settings = get_settings()

engine = create_async_engine(
    _settings.DATABASE_URL,
    echo=_settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()