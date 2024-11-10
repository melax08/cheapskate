from aiogram.filters.callback_data import CallbackData


class ExpenseCurrencyCallback(CallbackData, prefix="curc"):
    expense_id: int
    currency_id: int
