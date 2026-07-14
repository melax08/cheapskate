import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.category import Category
from backend.app.services.category import CategoryService
from tests.test_backend.factories.category import CategoryFactory


@pytest.fixture
async def category(db_session: AsyncSession) -> Category:
    return await CategoryFactory.create_async(db_session)


@pytest.fixture
async def category_service(db_session: AsyncSession) -> CategoryService:
    return CategoryService(db_session)
