# app/core/database.py

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from app.core.config import settings


Base = declarative_base()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Backward-compatible DB dependency used by app/api/deps.py
    """
    async with AsyncSessionLocal() as session:
        yield session


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Cleaner alias for route files that import get_db_session directly.
    """
    async for session in get_db():
        yield session


async def init_db() -> None:
    """
    Create database tables on startup for local development.
    """
    # Import all models explicitly so SQLAlchemy metadata is populated
    from app.models.users import User  # noqa: F401
    from app.models.otp import OTPCode  # noqa: F401
    from app.models.chats import Chat  # noqa: F401
    from app.models.documents import Document  # noqa: F401
    from app.models.chunks import DocumentChunk  # noqa: F401
    from app.models.messages import Message  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
