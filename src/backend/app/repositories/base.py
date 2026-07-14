from typing import Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession


class CreateRemoveMixin:
    async def create(self, obj_in, session: AsyncSession, additional_data: dict | None = None):
        """Creates DB object from pydantic schema."""
        obj_in_data = obj_in.model_dump()
        if additional_data is not None:
            obj_in_data.update(additional_data)
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


class UpdateMixin:
    async def update(
        self,
        db_obj,
        obj_in,
        session: AsyncSession,
    ):
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.model_dump(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj


class RepositoryBase(CreateRemoveMixin, UpdateMixin):
    """Class with base DB operations."""

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

    async def get_first_with_some_field_match(
        self, session: AsyncSession, instance_id_to_exclude: int | None = None, **kwargs: Any
    ):
        """Get first instance with some specified fields match."""
        or_statement = [getattr(self.model, key) == value for key, value in kwargs.items()]
        exclude_statement = []
        if instance_id_to_exclude is not None:
            exclude_statement = [self.model.id != instance_id_to_exclude]

        db_objs = await session.execute(
            select(self.model).where(or_(*or_statement), *exclude_statement)
        )
        return db_objs.scalars().first()


class SingletonRepositoryBase(CreateRemoveMixin, UpdateMixin):
    """Base class with DB operations for models with one instance."""

    def __init__(self, model):
        self.model = model

    async def get(self, session: AsyncSession):
        db_obj = await session.execute(select(self.model))
        return db_obj.scalars().first()
