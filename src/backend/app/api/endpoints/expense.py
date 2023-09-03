from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.category import CategoryDB
from app.schemas.expense import ExpenseCreate, ExpenseDB, MoneyLeft
from app.core.db import get_async_session
from app.crud.expense import expense_crud
from app.api.validators import check_category_exists, check_expense_exists
from app.core.config import settings

router = APIRouter()


@router.post('/', response_model=ExpenseDB)
async def add_expense(
        expense: ExpenseCreate,
        session: AsyncSession = Depends(get_async_session)
):
    """Add expense."""
    category = await check_category_exists(expense.category_id, session)
    category_pydantic = CategoryDB(id=category.id, name=category.name)
    new_expense = await expense_crud.create(expense, session)
    money_left = await expense_crud.calculate_money_left(session)
    new_expense = ExpenseDB(
        **new_expense.__dict__,
        category=category_pydantic,
        money_left=money_left
    )
    return new_expense


@router.delete('/{expense_id}', response_model=ExpenseDB)
async def delete_expense(
        expense_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    """Delete expense by expense id."""
    expense = await check_expense_exists(expense_id, session)
    category = await check_category_exists(expense.category_id, session)
    category_pydantic = CategoryDB(id=category.id, name=category.name)
    expense = await expense_crud.remove(expense, session)
    money_left = await expense_crud.calculate_money_left(session)
    expense = ExpenseDB(
        id=expense.__dict__['id'],
        amount=expense.__dict__['amount'],
        category=category_pydantic,
        money_left=money_left
    )
    return expense


@router.get('/money-left', response_model=MoneyLeft)
async def get_money_left(
    session: AsyncSession = Depends(get_async_session)
):
    money_left = await expense_crud.calculate_money_left(session)
    response_model = MoneyLeft(
        budget=settings.month_budget,
        money_left=money_left
    )
    return response_model
