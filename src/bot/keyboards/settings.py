from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.api_requests import APIClient
from bot.callbacks.settings import (
    ChangeBudgetCallback,
    ChangeDefaultCurrencyCallback,
    SelectDefaultCurrencyCallback,
)
from bot.constants.constants import CURRENCIES_NUMBER_IN_ROW


async def create_default_currency_keyboard(client: APIClient) -> InlineKeyboardMarkup:
    """Create keyboard wih currencies from API."""
    currencies = await client.get_currencies()

    if len(currencies) == 0:
        raise ValueError

    builder = InlineKeyboardBuilder()

    for currency in currencies:
        builder.button(
            text=currency["name"],
            callback_data=SelectDefaultCurrencyCallback(currency_id=currency.get("id")),
        )

    builder.adjust(CURRENCIES_NUMBER_IN_ROW)

    return builder.as_markup()


def create_settings_keyboard() -> InlineKeyboardMarkup:
    """Create settings keyboard markup."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Поменять валюту",
                    callback_data=ChangeDefaultCurrencyCallback().pack(),
                ),
                InlineKeyboardButton(
                    text="Поменять бюджет", callback_data=ChangeBudgetCallback().pack()
                ),
            ]
        ]
    )


settings_markup = create_settings_keyboard()
