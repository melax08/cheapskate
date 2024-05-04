"""
Initialize the default instances of currency and settings.
Use only outside the FastAPI application because multi workers.
"""

import asyncio

from sqlalchemy import select

from backend.app.core.db import AsyncSessionLocal
from backend.app.models import Currency, Setting

DEFAULT_CURRENCY: dict = {
    "name": "Американский доллар",
    "letter_code": "USD",
    "country": "Америка",
}

DEFAULT_BUDGET_VALUE: int | float = 1000


async def init_default_db_instances():
    """
    The application should have 1 currency instance and 1 settings instance
    on the first startup.
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Currency))
        currency = result.scalars().first()

        if not currency:
            currency = Currency(**DEFAULT_CURRENCY)
            session.add(currency)
            await session.commit()
            await session.refresh(currency)

        result = await session.execute(select(Setting))
        setting = result.scalars().first()

        if not setting:
            setting = Setting(
                budget=DEFAULT_BUDGET_VALUE, default_currency_id=currency.id
            )
            session.add(setting)
            await session.commit()


if __name__ == "__main__":
    asyncio.run(init_default_db_instances())
