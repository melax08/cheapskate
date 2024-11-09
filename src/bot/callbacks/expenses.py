from decimal import Decimal

from aiogram.filters.callback_data import CallbackData


class ExpenseCategoryCallback(CallbackData, prefix="exp"):
    amount: Decimal
    category_id: int


class ExpenseDeleteCallback(CallbackData, prefix="del"):
    expense_id: int


class ExpenseChangeCurrencyCallback(CallbackData, prefix="cur"):
    expense_id: int
    amount: Decimal
