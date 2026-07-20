from fastapi import APIRouter, Depends
from fastapi_pagination.cursor import CursorPage
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.db import get_async_session
from backend.app.dependencies.authorization import get_current_user
from backend.app.models.user import User
from backend.app.schemas.expense import ExpenseCreate, ExpenseDB, ExpenseMoneyLeftDB, ExpenseUpdate
from backend.app.services.expense import ExpenseService

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("", response_model=CursorPage[ExpenseDB])
async def expenses_list(
    expense_service: ExpenseService = Depends(ExpenseService),
    session: AsyncSession = Depends(get_async_session),
) -> CursorPage[ExpenseDB]:
    expenses = await expense_service.get_expenses()
    return await apaginate(session, expenses)


@router.get("/{expense_id}", response_model=ExpenseDB)
async def expenses_detail(
    expense_id: int, expense_service: ExpenseService = Depends(ExpenseService)
) -> ExpenseDB:
    return await expense_service.get_expense_by_id(expense_id)


@router.post("", response_model=ExpenseMoneyLeftDB)
async def expenses_create(
    expense_data: ExpenseCreate,
    user: User = Depends(get_current_user),
    expense_service: ExpenseService = Depends(ExpenseService),
) -> ExpenseMoneyLeftDB:
    return await expense_service.add_expense(expense_data, user)


@router.delete("/{expense_id}", response_model=ExpenseMoneyLeftDB)
async def expenses_delete(
    expense_id: int, expense_service: ExpenseService = Depends(ExpenseService)
) -> ExpenseMoneyLeftDB:
    return await expense_service.delete_expense(expense_id)


@router.patch("/{expense_id}", response_model=ExpenseDB)
async def expenses_partial_update(
    expense_id: int,
    expense_data: ExpenseUpdate,
    expense_service: ExpenseService = Depends(ExpenseService),
) -> ExpenseDB:
    return await expense_service.update_expense(expense_id, expense_data)
