import datetime as dt
from typing import Optional

from app.models import Category, Expense
from sqlalchemy import Integer, and_, desc, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import CRUDBase


class CRUDCategory(CRUDBase):
    """Class with DB CRUD operations for `Category` model."""

    async def get_category_by_name(
            self, category_name: str, session: AsyncSession
    ) -> Optional[Category]:
        db_obj = await session.execute(select(self.model).where(
            self.model.name == category_name)
        )
        return db_obj.scalars().first()

    @staticmethod
    async def _select_categories_expenses(
            session: AsyncSession, where_stmt: bool
    ):
        """Select the list of expenses by categories for specified period."""
        categories_expenses = await session.execute(select(
            Category.name,
            func.sum(Expense.amount).label('category_expense')
        ).join(Expense).where(where_stmt).group_by(
            Category.name).order_by(desc('category_expense')))

        return categories_expenses.all()

    async def get_today_expenses_by_categories(self, session: AsyncSession):
        """Gets the list of today expenses by categories."""
        return await self._select_categories_expenses(
            session,
            Expense.date >= dt.date.today()
        )

    async def get_this_month_expenses_by_categories(
            self, session: AsyncSession
    ):
        """Gets the list of this month expenses by categories."""
        return await self._select_categories_expenses(
            session,
            Expense.date >= dt.date(
                dt.date.today().year, dt.date.today().month, 1
            )
        )

    async def get_expenses_by_categories_for_period(
            self, year: int, month: int, session: AsyncSession
    ):
        """Get the list of expenses by categories for specified
        year and month."""
        return await self._select_categories_expenses(
            session,
            and_(
                func.cast(extract("month", Expense.date), Integer) == month,
                func.cast(extract("year", Expense.date), Integer) == year
            )
        )


category_crud = CRUDCategory(Category)
