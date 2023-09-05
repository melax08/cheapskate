import datetime as dt
from typing import Union

from app.core.config import settings
from app.models.expense import Expense
from sqlalchemy import Integer, and_, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import CRUDBase


class CRUDExpense(CRUDBase):
    """Class with DB CRUD operations for `Expense` model."""

    async def calculate_money_left(
            self, session: AsyncSession
    ) -> Union[float, int]:
        """Calculates how much money is left from the budget for
        the current month."""
        current_date = dt.datetime.now()

        waisted_money_for_current_month = await session.execute(
            select(func.sum(self.model.amount)).where(and_(
                func.cast(extract("month", self.model.date),
                          Integer) == current_date.month),
                func.cast(extract("year", self.model.date),
                          Integer) == current_date.year)
        )

        money_spend = waisted_money_for_current_month.scalars().first()

        if not money_spend:
            money_spend = 0
        money_left = settings.month_budget - money_spend

        return round(money_left, 2)


expense_crud = CRUDExpense(Expense)
