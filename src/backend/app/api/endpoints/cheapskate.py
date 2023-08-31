from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.cheapskate import (
    CategoryCreate,
    CategoryDB,
    ExpenseCreate,
    ExpenseDB
)
from app.core.db import get_async_session
from app.crud.cheapskate import get_multi, create, remove, calculate_money_left
from app.models.cheapskate import Category, Expense
from app.api.validators import check_category_exists, check_expense_exists

router = APIRouter()


@router.get('/category/', response_model=list[CategoryDB])
async def get_all_categories(
        session: AsyncSession = Depends(get_async_session)
):
    """Gets the all expense categories."""
    categories = await get_multi(Category, session)
    return categories


@router.post('/expense/', response_model=ExpenseDB)
async def add_expense(
        expense: ExpenseCreate,
        session: AsyncSession = Depends(get_async_session)
):
    """Add expense."""
    category = await check_category_exists(expense.category_id, session)
    category_pydantic = CategoryDB(id=category.id, name=category.name)
    new_expense = await create(Expense, expense, session)
    money_left = await calculate_money_left(session)
    new_expense = ExpenseDB(
        **new_expense.__dict__,
        category=category_pydantic,
        money_left=money_left
    )
    return new_expense


@router.delete('/expense/{expense_id}', response_model=ExpenseDB)
async def delete_expense(
        expense_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    """Delete expense by expense id."""
    expense = await check_expense_exists(expense_id, session)
    category = await check_category_exists(expense.category_id, session)
    category_pydantic = CategoryDB(id=category.id, name=category.name)
    expense = await remove(expense, session)
    money_left = await calculate_money_left(session)
    expense = ExpenseDB(
        id=expense.__dict__['id'],
        amount=expense.__dict__['amount'],
        category=category_pydantic,
        money_left=money_left
    )
    return expense


@router.get('/expense/money-left', response_model=int)
async def get_money_left(
    session: AsyncSession = Depends(get_async_session)
):
    money_left = await calculate_money_left(session)
    return money_left
