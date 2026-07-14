import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.user import User
from tests.test_backend.factories.user import UserFactory


@pytest.fixture
async def user(db_session: AsyncSession) -> User:
    return await UserFactory.create_async(session=db_session)
