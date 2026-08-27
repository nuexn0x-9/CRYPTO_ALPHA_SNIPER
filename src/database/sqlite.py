"""SQLite Database connection manager with WAL mode and async support."""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config.settings import get_settings

from .models import Base

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Gets or initializes the singleton AsyncEngine."""
    global _engine
    if _engine is None:
        settings = get_settings()

        # Ensure parent directory for database file exists
        if settings.DATABASE_URL.startswith("sqlite+aiosqlite:///"):
            db_path = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "")
            parent_dir = os.path.dirname(db_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)

        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            future=True,
        )
    return _engine


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """Gets or initializes the async session factory."""
    global _sessionmaker
    if _sessionmaker is None:
        engine = get_engine()
        _sessionmaker = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _sessionmaker


async def init_db() -> None:
    """Initializes tables and configures SQLite Pragmas for concurrency (WAL mode)."""
    engine = get_engine()
    settings = get_settings()

    async with engine.begin() as conn:
        # If using SQLite, enable WAL (Write-Ahead Logging) and Normal synchronous mode
        if "sqlite" in settings.DATABASE_URL:
            await conn.execute(text("PRAGMA journal_mode=WAL;"))
            await conn.execute(text("PRAGMA synchronous=NORMAL;"))
            await conn.execute(text("PRAGMA busy_timeout=5000;"))
            logger.info("Configured SQLite WAL mode and busy timeout.")

        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully.")


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provides a transactional async database session context."""
    session_factory = get_sessionmaker()
    session = session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
