import calendar
from collections import defaultdict

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.api_requests import APIClient
from bot.callbacks.statistic import MonthCallback, YearCallback
from bot.utils import get_russian_month_name


async def create_statistic_years_keyboard(
    client: APIClient,
) -> InlineKeyboardMarkup | None:
    """Create initial statistic keyboard with years and months in callback data."""
    periods = await client.get_expense_periods()

    if not periods:
        return None

    builder = InlineKeyboardBuilder()

    year_months_map = defaultdict(list)
    for period in periods:
        year_months_map[period["year"]].append(str(period["month"]))

    for year, months in year_months_map.items():
        builder.button(
            text=str(year),
            callback_data=YearCallback(year=year, months=",".join(months)),
        )

    builder.adjust(1)

    return builder.as_markup()


def create_statistic_months_keyboard(year: int, months: str) -> InlineKeyboardMarkup:
    """Create a keyboard with the months of the selected year in which the expenses
    occurred."""
    builder = InlineKeyboardBuilder()

    for month in months.split(","):
        month = int(month)
        builder.button(
            text=f"{get_russian_month_name(calendar.month_name[month])} {year}",
            callback_data=MonthCallback(year=year, month=month),
        )

    builder.adjust(1)

    return builder.as_markup()
