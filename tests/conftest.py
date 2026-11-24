from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession, create_async_engine

from app.config import settings
from app.db import Base, get_session
from main import app

TEST_USER = "tester"


@pytest.fixture
async def client(session: AsyncSession) -> AsyncIterator[AsyncClient]:
    # Routes get the rolled-back test session instead of a real one.
    app.dependency_overrides[get_session] = lambda: session
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", headers={"X-User": TEST_USER}
    ) as http:
        yield http
    app.dependency_overrides.clear()


@pytest.fixture
async def session(connection: AsyncConnection) -> AsyncIterator[AsyncSession]:
    # Routes call commit(); savepoint mode turns that into a savepoint release,
    # so the outer transaction stays open and the rollback below undoes everything.
    async with AsyncSession(
        bind=connection, expire_on_commit=False, join_transaction_mode="create_savepoint"
    ) as db_session:
        yield db_session


@pytest.fixture
async def connection(engine: AsyncEngine) -> AsyncIterator[AsyncConnection]:
    async with engine.connect() as conn:
        transaction = await conn.begin()
        yield conn
        await transaction.rollback()


@pytest.fixture(scope="session")
async def engine() -> AsyncIterator[AsyncEngine]:
    test_engine = create_async_engine(_test_database_url())
    async with test_engine.begin() as conn:
        # Fresh schema each run, matching current models (Alembic not involved).
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    await test_engine.dispose()


def _test_database_url() -> str:
    url = settings.test_database_url
    if not url:
        pytest.exit("TEST_DATABASE_URL is not set in .env", returncode=1)
    # Guard: drop_all on the dev database would wipe it.
    if url == settings.database_url:
        pytest.exit("TEST_DATABASE_URL must differ from DATABASE_URL", returncode=1)
    return url
