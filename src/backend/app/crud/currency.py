import datetime as dt

from sqlalchemy import Integer, and_, desc, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import Category, Currency, Expense

from .base import CRUDBase


class CRUDCurrency(CRUDBase):
    """Class with DB CRUD operations for `Currency` model."""

    @staticmethod
    async def _select_currencies_categories_expenses(
        session: AsyncSession, where_stmt: bool
    ):
        """Select the list of expenses by currencies and categories for specified
        period."""
        currencies_categories_expenses = await session.execute(
            select(
                Currency,
                Category,
                func.sum(Expense.amount).label("currency_category_expense"),
            )
            .join(Expense, Expense.currency_id == Currency.id)
            .join(Category, Expense.category_id == Category.id)
            .where(where_stmt)
            .group_by(Currency, Category)
            .order_by(desc("currency_category_expense"))
        )
        return currencies_categories_expenses.all()

    async def get_this_month_expenses_by_currencies_and_categories(
        self, session: AsyncSession
    ):
        """Gets the list of this month expenses by currencies and categories."""
        return await self.get_expenses_by_currencies_and_categories_for_period(
            dt.date.today().year, dt.date.today().month, session
        )

    async def get_today_expenses_by_currencies_and_categories(
        self, session: AsyncSession
    ):
        """Gets the list of today expenses by currencies and categories."""
        return await self._select_currencies_categories_expenses(
            session, Expense.date >= dt.date.today()
        )

    async def get_expenses_by_currencies_and_categories_for_period(
        self, year: int, month: int, session: AsyncSession
    ):
        """Get the list of expenses by currencies and categories for specified
        year and month."""
        return await self._select_currencies_categories_expenses(
            session,
            and_(
                func.cast(extract("month", Expense.date), Integer) == month,
                func.cast(extract("year", Expense.date), Integer) == year,
            ),
        )


currency_crud = CRUDCurrency(Currency)
