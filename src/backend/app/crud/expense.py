import datetime as dt
from typing import Union

from sqlalchemy import Integer, and_, desc, distinct, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.models.expense import Expense

from .base import CRUDBase


class CRUDExpense(CRUDBase):
    """Class with DB CRUD operations for `Expense` model."""

    def _get_period_stmt(self, year: int, month: int):
        return and_(
            func.cast(extract("month", self.model.date), Integer) == month,
            func.cast(extract("year", self.model.date), Integer) == year
        )

    async def calculate_money_expense_sum(
            self, where_stmt, session: AsyncSession
    ) -> Union[float, int]:
        """Calculates how much money was spent with specified
        WHERE statement."""
        money_spent = await session.execute(
            select(func.sum(self.model.amount)).where(where_stmt)
        )
        return money_spent.scalars().first() or 0

    async def calculate_money_left(
            self, session: AsyncSession
    ) -> Union[float, int]:
        """Calculates how much money is left from the budget for
        the current month."""
        current_date = dt.datetime.now()

        money_spent = await self.calculate_money_expense_sum(
            self._get_period_stmt(current_date.year, current_date.month),
            session
        )
        money_left = settings.month_budget - money_spent
        return round(money_left, 2)

    async def calculate_today_expenses(
            self, session: AsyncSession
    ) -> Union[float, int]:
        """Calculates how much money was spent today."""
        today_expenses = await self.calculate_money_expense_sum(
            self.model.date >= dt.date.today(),
            session
        )
        return round(today_expenses, 2)

    async def get_years_and_months_with_expenses(self, session: AsyncSession):
        """Gets unique years and months with expenses."""
        periods = await session.execute(
            select(
                distinct(extract("year", self.model.date)).label('year'),
                extract("month", self.model.date).label('month')
            ).order_by(desc('year'), desc('month'))
        )
        return periods.all()

    async def get_expenses_sum_for_year_month(
            self, year: int, month: int, session: AsyncSession
    ):
        """Get the amount of spent money for specified year and month."""
        money_spent = await self.calculate_money_expense_sum(
            self._get_period_stmt(year, month),
            session
        )
        return round(money_spent, 2)


expense_crud = CRUDExpense(Expense)
