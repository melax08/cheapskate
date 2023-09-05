from http import HTTPStatus

from app.crud.category import category_crud
from app.crud.expense import expense_crud
from app.models import Category, Expense
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


async def check_category_exists(
        category_id: int, session: AsyncSession) -> Category:
    category = await category_crud.get(category_id, session)
    if category is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Category not found'
        )
    return category


async def check_expense_exists(
        expense_id: int, session: AsyncSession) -> Expense:
    expense = await expense_crud.get(expense_id, session)
    if expense is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Expense not found'
        )
    return expense


async def check_category_name_duplicate(
        category_name: str, session: AsyncSession
) -> None:
    category = await category_crud.get_category_by_name(category_name, session)
    if category is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Category with that name already exists'
        )
