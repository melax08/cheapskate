import datetime as dt

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.validators import (
    check_currency_exists,
    check_expense_exists,
    validate_month_year,
)
from backend.app.core.db import get_async_session
from backend.app.crud import currency_crud, expense_crud, setting_crud
from backend.app.schemas.currency import CurrencySet
from backend.app.schemas.expense import (
    ExpenseCreate,
    ExpenseDB,
    ExpenseMoneyLeftDB,
    ExpensePeriod,
    ExpenseStatistic,
    MoneyLeftNew,
)
from backend.app.services.expense import ExpenseService
from configs.api_settings import (
    MONEY_LEFT_PATH,
    PERIOD_EXPENSE_PATH,
    STATISTIC_PATH,
    TODAY_EXPENSE_PATH,
)

router = APIRouter()


@router.post("/", response_model=ExpenseMoneyLeftDB)
async def add_expense(
    expense: ExpenseCreate, expense_service: ExpenseService = Depends(ExpenseService)
) -> ExpenseMoneyLeftDB:
    """Add expense."""
    return await expense_service.add_expense(expense)


@router.delete("/{expense_id}", response_model=ExpenseMoneyLeftDB)
async def delete_expense(
    expense_id: int, expense_service: ExpenseService = Depends(ExpenseService)
) -> ExpenseMoneyLeftDB:
    """Delete an expense by the expense id."""
    return await expense_service.delete_expense(expense_id)


@router.get(MONEY_LEFT_PATH, response_model=MoneyLeftNew)
async def get_money_left(session: AsyncSession = Depends(get_async_session)):
    """Gets information about month budget, money left for month,
    money spend in current month."""
    settings = await setting_crud.get_settings(session)
    budget = settings.budget
    default_currency = settings.default_currency
    money_left = await expense_crud.calculate_money_left(
        session=session, budget=budget, default_currency=default_currency
    )
    money_spent = round(budget - money_left, 2)

    expenses = await currency_crud.get_this_month_expenses_by_currencies_and_categories(session)

    return MoneyLeftNew.from_db_query(
        crud_result=expenses,
        budget=budget,
        money_left=money_left,
        money_spent=money_spent,
        current_datetime=dt.datetime.now(),
        default_currency=default_currency,
    )


@router.get(TODAY_EXPENSE_PATH, response_model=ExpenseStatistic)
async def get_today_expenses(session: AsyncSession = Depends(get_async_session)):
    """Gets information about today expenses."""
    expenses = await currency_crud.get_today_expenses_by_currencies_and_categories(session)
    return ExpenseStatistic.from_db_query(crud_result=expenses)


@router.get(PERIOD_EXPENSE_PATH, response_model=list[ExpensePeriod])
async def get_years_and_months_with_expenses(
    session: AsyncSession = Depends(get_async_session),
):
    """Gets the list of years and months with expenses."""
    periods = await expense_crud.get_years_and_months_with_expenses(session)
    periods = [ExpensePeriod(year=year, month=month) for year, month in periods]
    return periods


@router.post(STATISTIC_PATH, response_model=ExpenseStatistic)
async def get_statistic_for_period(
    period: ExpensePeriod,
    session: AsyncSession = Depends(get_async_session),
):
    """Get the information about expenses for specified month and year."""
    validate_month_year(period.year, period.month)
    expenses = await currency_crud.get_expenses_by_currencies_and_categories_for_period(
        period.year, period.month, session
    )
    return ExpenseStatistic.from_db_query(crud_result=expenses)


@router.post("/{expense_id}/currency", response_model=ExpenseDB)
async def set_currency(
    expense_id: int,
    currency: CurrencySet,
    session: AsyncSession = Depends(get_async_session),
):
    """Set specified currency for the specified expense."""
    expense = await check_expense_exists(expense_id, session)
    currency = await check_currency_exists(currency.currency_id, session)
    expense = await expense_crud.set_currency(expense, currency.id, session)
    return expense
