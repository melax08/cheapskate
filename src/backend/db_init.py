"""
Initialize the default instances of currency and settings.
Use only outside the FastAPI application because multi workers.
"""

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.core.db import AsyncSessionLocal
from backend.app.models import Currency, Report, Setting

DEFAULT_CURRENCY: dict = {
    "name": "Американский доллар",
    "letter_code": "USD",
    "country": "Америка",
}

DEFAULT_BUDGET_VALUE: int | float = 1000


async def init_default_currency(session: AsyncSession) -> Currency:
    """Initialize default application currency."""
    result = await session.execute(select(Currency))
    currency = result.scalars().first()

    if not currency:
        currency = Currency(**DEFAULT_CURRENCY)
        session.add(currency)
        await session.commit()
        await session.refresh(currency)

    return currency


async def init_default_settings(session: AsyncSession, default_currency_id: int) -> None:
    """Initialize default application settings instance."""
    result = await session.execute(select(Setting))
    setting = result.scalars().first()

    if not setting:
        setting = Setting(budget=DEFAULT_BUDGET_VALUE, default_currency_id=default_currency_id)
        session.add(setting)
        await session.commit()


async def init_default_report(session: AsyncSession) -> None:
    """Initialize default application report instance."""
    if settings.report_spreadsheet_id:
        result = await session.execute(select(Report))
        report = result.scalars().first()

        if not report:
            report = Report(spreadsheet_id=settings.report_spreadsheet_id)
            session.add(report)
            await session.commit()


async def init_default_db_instances():
    """
    The application should have 1 currency instance, 1 settings instance and, probably,
    1 report instance on the first startup.
    """
    async with AsyncSessionLocal() as session:
        currency = await init_default_currency(session)
        await init_default_settings(session, currency.id)
        await init_default_report(session)


if __name__ == "__main__":
    asyncio.run(init_default_db_instances())
