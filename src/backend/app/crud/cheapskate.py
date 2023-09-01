import datetime as dt

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, Integer, extract, and_

from app.models import Expense
from app.core.constants import BUDGET_FOR_MONTH


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


async def remove(db_obj, session: AsyncSession):
    await session.delete(db_obj)
    await session.commit()
    return db_obj


async def calculate_money_left(session: AsyncSession):
    """
    Calculates how much money is left from the budget for the current month.
    """
    current_date = dt.datetime.now()
    waisted_money_for_current_month = await session.execute(
        select(func.sum(Expense.amount)).where(and_(
            func.cast(extract("month", Expense.date),
                      Integer) == current_date.month),
            func.cast(extract("year", Expense.date),
                      Integer) == current_date.year)
    )
    money_spend = waisted_money_for_current_month.scalars().first()
    if not money_spend:
        money_spend = 0
    money_left = BUDGET_FOR_MONTH - money_spend
    return money_left
