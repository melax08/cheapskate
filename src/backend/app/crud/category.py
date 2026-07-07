from sqlalchemy import exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import Category, Expense

from .base import CRUDBase


class CRUDCategory(CRUDBase):
    """Class with DB CRUD operations for `Category` model."""

    async def get_category_by_name(
        self, category_name: str, session: AsyncSession
    ) -> Category | None:
        db_obj = await session.execute(select(self.model).where(self.model.name == category_name))
        return db_obj.scalars().first()

    async def get_all_categories(self, only_visible: bool, session: AsyncSession):
        if only_visible:
            db_objs = await session.execute(select(self.model).where(self.model.is_visible == True))  # noqa
        else:
            db_objs = await session.execute(select(self.model))

        return db_objs.scalars().all()

    async def get_all_categories_with_expenses_count(self, session: AsyncSession):
        db_objs = await session.execute(
            select(self.model, func.count(Expense.id).label("expenses_count"))
            .outerjoin(Expense, Expense.category_id == Category.id)
            .group_by(Category.id)
        )
        return db_objs

    async def is_category_has_expenses(self, category: Category, session: AsyncSession) -> bool:
        return await session.scalar(select(exists().where(Expense.category_id == category.id)))


category_crud = CRUDCategory(Category)
