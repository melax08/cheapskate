import pytest
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from api import app
from backend.app.core.config import settings
from backend.app.core.db import Base, get_async_session

TEST_DB_URL = f"{settings.database_url}/test_db"

# ToDo: сделать автоматическое создание test_db при старте тестов

engine = create_async_engine(
    TEST_DB_URL,
    echo=False,
)

SessionTest = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session():
    async with engine.connect() as connection:
        transaction = await connection.begin()

        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
        )

        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()


@pytest.fixture
async def override_db(db_session):
    async def _get_db():
        yield db_session

    app.dependency_overrides[get_async_session] = _get_db

    yield

    app.dependency_overrides.clear()
