import datetime as dt

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, Integer, extract, and_

from .base import CRUDBase
from app.core.constants import BUDGET_FOR_MONTH
from app.models.expense import Expense


class CRUDExpense(CRUDBase):
    """Class with DB CRUD operations for `Expense` model."""

    async def calculate_money_left(self, session: AsyncSession) -> int:
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
        money_left = BUDGET_FOR_MONTH - money_spend

        return money_left


expense_crud = CRUDExpense(Expense)
