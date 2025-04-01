import datetime as dt

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.validators import validate_month_year
from backend.app.core.db import get_async_session
from backend.app.crud import currency_crud, expense_crud, setting_crud
from backend.app.schemas.statistic import MoneyLeft, Statistic, StatisticPeriod


class StatisticService:
    """Service to get the expense statistics."""

    def __init__(self, session: AsyncSession = Depends(get_async_session)) -> None:
        self._session = session

    async def get_money_left(self) -> MoneyLeft:
        """Get the information about the current month money left."""
        settings = await setting_crud.get_settings(self._session)
        money_left = await expense_crud.calculate_money_left(
            session=self._session,
            budget=settings.budget,
            default_currency=settings.default_currency,
        )
        expenses = await currency_crud.get_this_month_expenses_by_currencies_and_categories(
            self._session
        )

        return MoneyLeft.from_db_query(
            crud_result=expenses,
            budget=settings.budget,
            money_left=money_left,
            money_spent=round(settings.budget - money_left, 2),
            current_datetime=dt.datetime.now(),
            default_currency=settings.default_currency,
        )

    async def get_today_expenses(self) -> Statistic:
        """Get the information about today expenses by currencies and categories."""
        expenses = await currency_crud.get_today_expenses_by_currencies_and_categories(
            self._session
        )
        return Statistic.from_db_query(crud_result=expenses)

    async def get_statistic_periods(self) -> list[StatisticPeriod]:
        """Get periods with expenses."""
        periods = await expense_crud.get_years_and_months_with_expenses(self._session)
        return [StatisticPeriod(year=year, month=month) for year, month in periods]

    async def get_statistic_for_period(self, period: StatisticPeriod) -> Statistic:
        """Get the information about expenses by currencies and categories
        for the specified period."""
        validate_month_year(period.year, period.month)
        expenses = await currency_crud.get_expenses_by_currencies_and_categories_for_period(
            period.year, period.month, self._session
        )
        return Statistic.from_db_query(crud_result=expenses)
