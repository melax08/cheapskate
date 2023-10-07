import calendar
from typing import Optional, Union

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.api_requests import get_api_client
from bot.constants.constants import BUTTON_ROW_LEN


async def create_category_keyboard(
        money: Union[float, int]
) -> InlineKeyboardMarkup:
    """Create keyboard with categories from API."""
    async with get_api_client() as client:
        categories = await client.get_categories()

    if len(categories) == 0:
        raise ValueError

    keyboard = []
    row = []

    for category in categories:
        row.append(
            InlineKeyboardButton(
                category['name'], callback_data=f'{money} {category["id"]}'
            )
        )
        if len(row) == BUTTON_ROW_LEN:
            keyboard.append(row)
            row = []
    if len(row) > 0:
        keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)


async def create_expense_periods_keyboard() -> Optional[InlineKeyboardMarkup]:
    """Create keyboard with expense periods from API."""
    async with get_api_client() as client:
        periods = await client.get_expense_periods()

    if not periods:
        return None

    keyboard = []
    for period in periods:
        keyboard.append(InlineKeyboardButton(
            f'{calendar.month_abbr[period.get("month")]} {period.get("year")}',
            callback_data=f'REP {period.get("year")} {period.get("month")}')
        )

    return InlineKeyboardMarkup([keyboard])


def create_delete_expense_keyboard(expense_id: int) -> InlineKeyboardMarkup:
    """Creates delete expense button."""
    return InlineKeyboardMarkup.from_row(
        [InlineKeyboardButton('Удалить', callback_data=f'DEL {expense_id}')])
