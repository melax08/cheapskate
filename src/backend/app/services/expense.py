from backend.app.api.validators import (
    check_category_exists,
    check_currency_exists,
    check_expense_exists,
)
from backend.app.crud import expense_crud, setting_crud
from backend.app.schemas.category import CategoryDB
from backend.app.schemas.currency import CurrencyDB
from backend.app.schemas.expense import ExpenseCreate, ExpenseMoneyLeftDB
from backend.app.services.base import BaseService


class ExpenseService(BaseService):
    """Service to manage expenses business logic."""

    async def add_expense(self, expense_obj: ExpenseCreate) -> ExpenseMoneyLeftDB:
        """Create an expense record in the database, calculate how much money left in the monthly
        budget and return it."""
        await check_category_exists(expense_obj.category_id, self._session)

        if expense_obj.currency_id is not None:
            await check_currency_exists(expense_obj.currency_id, self._session)
        else:
            default_currency = await setting_crud.get_default_currency(self._session)
            expense_obj.currency_id = default_currency.id

        expense = await expense_crud.create(expense_obj, self._session)
        expense.money_left = await expense_crud.calculate_money_left(self._session)
        return expense

    async def delete_expense(self, expense_id: int) -> ExpenseMoneyLeftDB:
        """Delete an expense from the database by the specified id."""
        expense = await check_expense_exists(expense_id, self._session)

        category = CategoryDB(id=expense.category.id, name=expense.category.name)
        currency = (
            CurrencyDB(
                id=expense.currency.id,
                name=expense.currency.name,
                letter_code=expense.currency.letter_code,
                country=expense.currency.country,
            )
            if expense.currency
            else None
        )

        expense = await expense_crud.remove(expense, self._session)
        expense.money_left = await expense_crud.calculate_money_left(self._session)
        return ExpenseMoneyLeftDB(
            id=expense.id,
            amount=expense.amount,
            category=category,
            currency=currency,
            money_left=expense.money_left,
        )
