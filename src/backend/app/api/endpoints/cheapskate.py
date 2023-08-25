from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.cheapskate import (
    CategoryCreate,
    CategoryDB,
    ExpenseCreate,
    ExpenseDB
)
from app.core.db import get_async_session
from app.crud.cheapskate import get_multi, create
from app.models.cheapskate import Category, Expense
from app.api.validators import check_category_exists

router = APIRouter()


@router.get('/category', response_model=list[CategoryDB])
async def get_all_categories(
        session: AsyncSession = Depends(get_async_session)
):
    """Gets the all expense categories."""
    categories = await get_multi(Category, session)
    return categories


@router.post('/expense', response_model=ExpenseDB)
async def add_expense(
        expense: ExpenseCreate,
        session: AsyncSession = Depends(get_async_session)
):
    """Add expense."""
    # ToDo: добавить в возвращаемые данные money_left - остаток средств на этот месяц.
    await check_category_exists(expense.category_id, session)
    new_expense = await create(Expense, expense, session)
    return new_expense
