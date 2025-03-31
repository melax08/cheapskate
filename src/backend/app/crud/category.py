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


category_crud = CRUDCategory(Category)
