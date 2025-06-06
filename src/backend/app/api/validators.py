import datetime as dt
from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.crud import category_crud, currency_crud, expense_crud
from backend.app.models import Category, Currency, Expense
from backend.app.schemas.currency import CurrencyCreate


async def check_category_exists(category_id: int, session: AsyncSession) -> Category:
    """Checks if category exists in database."""
    category = await category_crud.get(category_id, session)
    if category is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Category not found")
    return category


async def check_expense_exists(expense_id: int, session: AsyncSession) -> Expense:
    """Checks if expense exists in database."""
    expense = await expense_crud.get(expense_id, session)
    if expense is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Expense not found")
    return expense


async def check_category_name_duplicate(category_name: str, session: AsyncSession) -> None:
    """Checks if category name already exists in database."""
    category = await category_crud.get_category_by_name(category_name, session)
    if category is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Category with that name already exists",
        )


def validate_month_year(year: int, month: int) -> None:
    """Checks if the month and year are correct."""
    try:
        dt.datetime.strptime(f"{month} {year}", "%m %Y")
    except ValueError as error:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Bad month/year") from error


async def check_currency_exists(currency_id: int, session: AsyncSession) -> Currency:
    """Checks if currency with specified id exists in database."""
    currency = await currency_crud.get(currency_id, session)
    if currency is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Currency not found")
    return currency


async def check_currency_unique_fields(currency: CurrencyCreate, session: AsyncSession) -> None:
    """Check is some currency already exists with the specified unique fields."""
    currency = await currency_crud.get_first_with_some_field_match(
        session,
        name=currency.name,
        letter_code=currency.letter_code,
        country=currency.country,
    )
    if currency:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Not unique name/letter_code/country"
        )
