from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import Category

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


category_crud = CRUDCategory(Category)
