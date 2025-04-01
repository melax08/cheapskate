from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.validators import (
    check_currency_exists,
    check_expense_exists,
)
from backend.app.core.db import get_async_session
from backend.app.crud import expense_crud
from backend.app.schemas.currency import CurrencySet
from backend.app.schemas.expense import (
    ExpenseCreate,
    ExpenseDB,
    ExpenseMoneyLeftDB,
)
from backend.app.services.expense import ExpenseService

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
