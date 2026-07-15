import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.currency import Currency
from tests.test_backend.factories.currency import CurrencyFactory


@pytest.fixture
async def currency(db_session: AsyncSession) -> Currency:
    return await CurrencyFactory.create_async(db_session)
