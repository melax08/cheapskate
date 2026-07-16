import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.currency import Currency
from backend.app.models.setting import Setting


@pytest.fixture
async def setting(db_session: AsyncSession, currency: Currency) -> Setting:
    setting = Setting(budget=10000, default_currency_id=currency.id)
    db_session.add(setting)
    await db_session.commit()
    return setting
