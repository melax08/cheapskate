from backend.app.api.validators import (
    check_category_exists,
    check_currency_exists,
    check_expense_exists,
    check_user_exists,
)
from backend.app.models import Expense, User
from backend.app.repositories import expense_repository, setting_repository
from backend.app.schemas.category import CategoryDB
from backend.app.schemas.currency import CurrencyDB
from backend.app.schemas.expense import (
    ExpenseCreate,
    ExpenseCreateWithUser,
    ExpenseMoneyLeftDB,
    ExpenseUpdate,
)
from backend.app.services.base import BaseService


class ExpenseService(BaseService):
    """Service to manage expenses business logic."""

    async def add_expense(
        self, expense_obj: ExpenseCreateWithUser | ExpenseCreate, user: User | None = None
    ) -> Expense:
        """Create an expense record in the database, calculate how much money left in the monthly
        budget and return it."""
        await check_category_exists(expense_obj.category_id, self._session)
        user_data = {}
        if user:
            user_data = {"user": user}
        else:
            if getattr(expense_obj, "user_telegram_id", None) is not None:
                user = await check_user_exists(expense_obj.user_telegram_id, self._session)
                delattr(expense_obj, "user_telegram_id")
                user_data = {"user": user}

        if expense_obj.currency_id is not None:
            await check_currency_exists(expense_obj.currency_id, self._session)
        else:
            default_currency = await setting_repository.get_default_currency(self._session)
            expense_obj.currency_id = default_currency.id

        expense = await expense_repository.create(
            expense_obj, self._session, additional_data=user_data
        )
        expense.money_left = await expense_repository.calculate_money_left(self._session)
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

        expense = await expense_repository.remove(expense, self._session)
        expense.money_left = await expense_repository.calculate_money_left(self._session)
        return ExpenseMoneyLeftDB(
            id=expense.id,
            amount=expense.amount,
            category=category,
            currency=currency,
            money_left=expense.money_left,
        )

    async def get_expenses(self) -> list[Expense]:
        return await expense_repository.get_multi(
            self._session, order_by=(Expense.id.desc(),), only_statement=True
        )

    async def get_expense_by_id(self, expense_id: int) -> Expense:
        return await check_expense_exists(expense_id, self._session)

    async def update_expense(self, expense_id: int, expense_data: ExpenseUpdate) -> Expense:
        expense = await check_expense_exists(expense_id, self._session)
        if expense_data.currency_id is not None and expense_data.currency_id != expense.currency_id:
            await check_currency_exists(expense_data.currency_id, self._session)
        if expense_data.category_id is not None and expense_data.category_id != expense.currency_id:
            await check_category_exists(expense_data.category_id, self._session)

        return await expense_repository.update(expense, expense_data, self._session)
