from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


async def get_multi(model, session: AsyncSession):
    db_objs = await session.execute(select(model))
    return db_objs.scalars().all()


async def get(model, obj_id: int, session: AsyncSession):
    db_obj = await session.execute(select(model).where(model.id == obj_id))
    return db_obj.scalars().first()


async def create(model, obj_in, session: AsyncSession):
    obj_in_data = obj_in.dict()
    db_obj = model(**obj_in_data)
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj
