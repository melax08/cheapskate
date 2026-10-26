from fastapi import APIRouter, Depends, status
from fastapi_pagination.cursor import CursorPage
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.db import get_async_session
from backend.app.dependencies.authorization import get_current_user
from backend.app.models.user import User
from backend.app.schemas.expense import (
    ExpenseCreate,
    ExpenseDB,
    ExpenseDBOnlyIds,
    ExpenseMoneyLeftDB,
    ExpenseUpdate,
)
from backend.app.services.expense import ExpenseService
from backend.app.utils import send_message_to_authorized_users_about_user_action

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("", response_model=CursorPage[ExpenseDBOnlyIds])
async def expenses_list(
    expense_service: ExpenseService = Depends(ExpenseService),
    session: AsyncSession = Depends(get_async_session),
    category: int | None = None,
    user: int | None = None,
    currency: int | None = None,
) -> CursorPage[ExpenseDBOnlyIds]:
    filters = {}
    if category is not None:
        filters["category_id"] = category
    if user is not None:
        filters["user_id"] = user
    if currency is not None:
        filters["currency_id"] = currency

    expenses = await expense_service.get_expenses(filters=filters)
    return await apaginate(session, expenses)


@router.get("/{expense_id}", response_model=ExpenseDB)
async def expenses_detail(
    expense_id: int, expense_service: ExpenseService = Depends(ExpenseService)
) -> ExpenseDB:
    return await expense_service.get_expense_by_id(expense_id)


@router.post("", response_model=ExpenseMoneyLeftDB, status_code=status.HTTP_201_CREATED)
async def expenses_create(
    expense_data: ExpenseCreate,
    user: User = Depends(get_current_user),
    expense_service: ExpenseService = Depends(ExpenseService),
) -> ExpenseMoneyLeftDB:
    expense = await expense_service.add_expense(expense_data, user)
    message = (
        f"✅ добавлена трата <b>{expense.amount.normalize():f} "
        f"{expense.currency.symbol or expense.currency.letter_code}</b> в категорию "
        f"<b>{expense.category.name}</b>"
    )
    if expense.description:
        message = message + f", описание: <b>{expense.description}</b>"
    await send_message_to_authorized_users_about_user_action(user, message)
    return expense


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
