from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.api_requests import APIClient
from bot.callbacks.currencies import ExpenseCurrencyCallback
from bot.constants.constants import CURRENCIES_NUMBER_IN_ROW


async def create_currency_keyboard(
    expense_id: int, client: APIClient
) -> InlineKeyboardMarkup:
    """Create keyboard wih currencies from API."""
    currencies = await client.get_currencies()

    if len(currencies) == 0:
        raise ValueError

    builder = InlineKeyboardBuilder()

    for currency in currencies:
        builder.button(
            text=currency["name"],
            callback_data=ExpenseCurrencyCallback(
                expense_id=expense_id, currency_id=currency.get("id")
            ),
        )

    builder.adjust(CURRENCIES_NUMBER_IN_ROW)

    return builder.as_markup()
