import asyncio
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.api.deps import get_db_session, get_current_user
from app.core.database import Base

# In-memory SQLite shared across the same process
TEST_DATABASE_URL = "sqlite+aiosqlite://"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def override_get_db_session():
    async with TestingSessionLocal() as session:
        yield session


def override_get_current_user():
    # Lightweight fake user object.
    # Your routes only need current_user.id for chats,
    # so this is enough for now.
    return SimpleNamespace(
        id="test-user-id",
        email="test@example.com",
    )


@pytest.fixture(scope="function", autouse=True)
def setup_test_db():
    async def _setup():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(_setup())


@pytest.fixture(scope="function")
def client():
    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()