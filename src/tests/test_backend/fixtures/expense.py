import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.expense import Expense
from tests.test_backend.factories.expense import ExpenseFactory


@pytest.fixture
async def expense(db_session: AsyncSession) -> Expense:
    return await ExpenseFactory.create_async(session=db_session)
