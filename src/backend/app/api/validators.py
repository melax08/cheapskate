from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.cheapskate import get
from app.models import Category, Expense


async def check_category_exists(
        category_id: int, session: AsyncSession) -> Category:
    category = await get(Category, category_id, session)
    if category is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Category not found'
        )
    return category


async def check_expense_exists(
        expense_id: int, session: AsyncSession) -> Expense:
    expense = await get(Expense, expense_id, session)
    if expense is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Expense not found'
        )
    return expense
