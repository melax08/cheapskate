import datetime as dt

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.validators import (check_category_exists,
                                        check_expense_exists,
                                        validate_month_year)
from backend.app.core.config import settings
from backend.app.core.db import get_async_session
from backend.app.crud import category_crud, expense_crud
from backend.app.schemas.category import CategoryDB
from backend.app.schemas.expense import (CategoryExpense, ExpenseCreate,
                                         ExpenseDB, ExpensePeriod,
                                         ExpenseStatistic, MoneyLeft)
from utils.api_settings import (MONEY_LEFT_PATH, PERIOD_EXPENSE_PATH,
                                STATISTIC_PATH, TODAY_EXPENSE_PATH)

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


@router.get(MONEY_LEFT_PATH, response_model=MoneyLeft)
async def get_money_left(
    session: AsyncSession = Depends(get_async_session)
):
    """Gets information about month budget, money left for month,
    money spend in current month."""
    money_left = await expense_crud.calculate_money_left(session)
    money_spend = round(settings.month_budget - money_left, 2)

    categories = await category_crud.get_this_month_expenses_by_categories(
        session)
    categories = [CategoryExpense(name=name, amount=amount)
                  for name, amount in categories]

    response_model = MoneyLeft(
        budget=settings.month_budget,
        money_left=money_left,
        money_spent=money_spend,
        current_datetime=dt.datetime.now(),
        categories=categories
    )
    return response_model


@router.get(TODAY_EXPENSE_PATH, response_model=ExpenseStatistic)
async def get_today_expenses(
        session: AsyncSession = Depends(get_async_session)
):
    """Gets information about today expenses."""
    today_expenses_amount = await expense_crud.calculate_today_expenses(
        session)
    today_categories = await category_crud.get_today_expenses_by_categories(
        session)

    categories = [CategoryExpense(name=name, amount=amount)
                  for name, amount in today_categories]

    response_model = ExpenseStatistic(
        money_spent=today_expenses_amount,
        categories=categories
    )

    return response_model


@router.get(PERIOD_EXPENSE_PATH, response_model=list[ExpensePeriod])
async def get_years_and_months_with_expenses(
        session: AsyncSession = Depends(get_async_session)
):
    """Gets the list of years and months with expenses."""
    periods = await expense_crud.get_years_and_months_with_expenses(session)
    periods = [
        ExpensePeriod(year=year, month=month) for year, month in periods
    ]
    return periods


@router.post(STATISTIC_PATH, response_model=ExpenseStatistic)
async def get_statistic_for_period(
        period: ExpensePeriod,
        session: AsyncSession = Depends(get_async_session),
):
    """Get the information about expenses for specified month and year."""
    validate_month_year(period.year, period.month)

    money_spent = await expense_crud.get_expenses_sum_for_year_month(
        period.year, period.month, session
    )

    categories = await category_crud.get_expenses_by_categories_for_period(
        period.year, period.month, session)
    categories = [CategoryExpense(name=name, amount=amount)
                  for name, amount in categories]

    response_model = ExpenseStatistic(
        money_spent=money_spent,
        categories=categories
    )
    return response_model
