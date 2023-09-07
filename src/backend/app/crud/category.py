import datetime as dt
from typing import Optional

from app.models import Category, Expense
from sqlalchemy import desc, func, select
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
    async def get_today_expenses_by_categories(session: AsyncSession):
        """Gets the list of today expenses by categories."""
        today_categories_with_expenses = await session.execute(select(
            Category.name,
            func.sum(Expense.amount).label('category_expense')
        ).join(Expense).where(Expense.date >= dt.date.today()).group_by(
            Category.name).order_by(desc('category_expense')))
        return today_categories_with_expenses.all()


category_crud = CRUDCategory(Category)
