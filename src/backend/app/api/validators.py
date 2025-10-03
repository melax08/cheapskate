import datetime as dt

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.crud import category_crud, currency_crud, expense_crud
from backend.app.models import Category, Currency, Expense
from backend.app.schemas.currency import CurrencyCreate
from backend.app.utils import raise_api_error
from configs.enums import APIErrorCode


async def check_category_exists(category_id: int, session: AsyncSession) -> Category:
    """Checks if category exists in database."""
    category = await category_crud.get(category_id, session)
    if category is None:
        raise_api_error(
            error_code=APIErrorCode.CATEGORY_NOT_FOUND,
            message="Категория не найдена",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return category


async def check_expense_exists(expense_id: int, session: AsyncSession) -> Expense:
    """Checks if expense exists in database."""
    expense = await expense_crud.get(expense_id, session)
    if expense is None:
        raise_api_error(
            error_code=APIErrorCode.EXPENSE_NOT_FOUND,
            message="Трата не найдена",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return expense


async def check_category_name_duplicate(category_name: str, session: AsyncSession) -> None:
    """Checks if category name already exists in database."""
    category = await category_crud.get_category_by_name(category_name, session)
    if category is not None:
        raise_api_error(
            error_code=APIErrorCode.CATEGORY_EXISTS,
            message="Категория с таким названием уже существует",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


def validate_month_year(year: int, month: int) -> None:
    """Checks if the month and year are correct."""
    try:
        dt.datetime.strptime(f"{month} {year}", "%m %Y")
    except ValueError:
        raise_api_error(
            error_code=APIErrorCode.BAD_MONTH_YEAR,
            message="Некорректный месяц/год",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


async def check_currency_exists(currency_id: int, session: AsyncSession) -> Currency:
    """Checks if currency with specified id exists in database."""
    currency = await currency_crud.get(currency_id, session)
    if currency is None:
        raise_api_error(
            error_code=APIErrorCode.CURRENCY_NOT_FOUND,
            message="Валюта не найдена",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
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
        raise_api_error(
            error_code=APIErrorCode.NOT_UNIQUE_CURRENCY_FIELDS,
            message="Не уникальное название/код/страна",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
