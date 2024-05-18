import datetime as dt

from configs.api_settings import (
    MONEY_LEFT_PATH,
    PERIOD_EXPENSE_PATH,
    STATISTIC_PATH,
    TODAY_EXPENSE_PATH,
)
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.validators import (
    check_category_exists,
    check_currency_exists,
    check_expense_exists,
    validate_month_year,
)
from backend.app.core.db import get_async_session
from backend.app.crud import currency_crud, expense_crud, setting_crud
from backend.app.schemas.category import CategoryDB
from backend.app.schemas.currency import CurrencyDB, CurrencySet
from backend.app.schemas.expense import (
    ExpenseCreate,
    ExpenseDB,
    ExpenseMoneyLeftDB,
    ExpensePeriod,
    ExpenseStatistic,
    MoneyLeftNew,
)

router = APIRouter()


@router.post("/", response_model=ExpenseMoneyLeftDB)
async def add_expense(
    expense: ExpenseCreate, session: AsyncSession = Depends(get_async_session)
):
    """Add expense."""
    await check_category_exists(expense.category_id, session)
    if expense.currency_id is not None:
        await check_currency_exists(expense.currency_id, session)
    else:
        default_currency = await setting_crud.get_default_currency(session)
        expense.currency_id = default_currency.id
    expense = await expense_crud.create(expense, session)
    money_left = await expense_crud.calculate_money_left(session)
    expense.__dict__["money_left"] = money_left
    return expense


@router.delete("/{expense_id}", response_model=ExpenseMoneyLeftDB)
async def delete_expense(
    expense_id: int, session: AsyncSession = Depends(get_async_session)
):
    """Delete expense by expense id."""
    expense = await check_expense_exists(expense_id, session)

    category = CategoryDB(
        id=expense.__dict__["category"].id, name=expense.__dict__["category"].name
    )
    currency = (
        CurrencyDB(
            id=expense.__dict__["currency"].id,
            name=expense.__dict__["currency"].name,
            letter_code=expense.__dict__["currency"].letter_code,
            country=expense.__dict__["currency"].country,
        )
        if expense.currency
        else None
    )

    await expense_crud.remove(expense, session)
    money_left = await expense_crud.calculate_money_left(session)
    response_data = ExpenseMoneyLeftDB(
        id=expense.__dict__["id"],
        amount=expense.__dict__["amount"],
        category=category,
        currency=currency,
        money_left=money_left,
    )
    return response_data


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

    expenses = await currency_crud.get_this_month_expenses_by_currencies_and_categories(
        session
    )

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
    expenses = await currency_crud.get_today_expenses_by_currencies_and_categories(
        session
    )
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
