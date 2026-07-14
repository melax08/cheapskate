from typing import Any, TypeVar

from factory.alchemy import SQLAlchemyModelFactory
from sqlalchemy.ext.asyncio import AsyncSession

ModelT = TypeVar("ModelT")


class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True

    @classmethod
    async def create_async(
        cls,
        session: AsyncSession,
        **kwargs: Any,
    ) -> ModelT:
        instance = cls.build(**kwargs)

        session.add(instance)
        await session.flush()

        return instance

    @classmethod
    async def create_batch_async(
        cls,
        session: AsyncSession,
        size: int,
        **kwargs: Any,
    ) -> list[ModelT]:
        instances = cls.build_batch(size, **kwargs)

        session.add_all(instances)
        await session.flush()

        return instances
