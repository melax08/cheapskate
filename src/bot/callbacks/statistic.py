from aiogram.filters.callback_data import CallbackData


class YearCallback(CallbackData, prefix="year"):
    year: int
    months: str


class MonthCallback(CallbackData, prefix="month"):
    year: int
    month: int
