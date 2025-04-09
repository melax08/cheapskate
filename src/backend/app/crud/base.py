from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDBase:
    """Class with base DB CRUD operations."""

    def __init__(self, model):
        self.model = model

    async def get(self, obj_id: int, session: AsyncSession):
        """Gets single DB object by id."""
        db_obj = await session.execute(select(self.model).where(self.model.id == obj_id))
        return db_obj.scalars().first()

    async def get_multi(self, session: AsyncSession):
        """Gets all DB objects from specified model."""
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    async def create(self, obj_in, session: AsyncSession):
        """Creates DB object from pydantic schema."""
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    @staticmethod
    async def remove(db_obj, session: AsyncSession):
        """Removes specified DB object."""
        await session.delete(db_obj)
        await session.commit()
        return db_obj

    async def get_first_with_some_field_match(self, session: AsyncSession, **kwargs: Any):
        """Get first instance with some specified fields match."""
        statement = [getattr(self.model, key) == value for key, value in kwargs.items()]
        db_objs = await session.execute(select(self.model).where(or_(*statement)))
        return db_objs.scalars().first()
