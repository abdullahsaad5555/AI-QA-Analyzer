# app/core/database.py

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # set to False in production if you don't want SQL logs
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a DB session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """
    Create all tables.
    Useful for local development before adding Alembic migrations.
    """
    from app.models import (  # noqa: F401
        User,
        EmailOTP,
        Chat,
        Document,
        DocumentChunk,
        Message,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
