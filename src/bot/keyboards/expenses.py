from decimal import Decimal

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.api_requests import APIClient
from bot.callbacks.expenses import (
    ExpenseCategoryCallback,
    ExpenseChangeCurrencyCallback,
    ExpenseDeleteCallback,
)
from bot.constants.constants import CATEGORIES_NUMBER_IN_ROW


async def create_category_keyboard(
    expense_amount: Decimal, client: APIClient
) -> InlineKeyboardMarkup:
    """Create keyboard with categories from API."""
    categories = await client.get_categories(only_visible=True)

    if len(categories) == 0:
        raise ValueError

    builder = InlineKeyboardBuilder()

    for category in categories:
        builder.button(
            text=category["name"],
            callback_data=ExpenseCategoryCallback(
                amount=expense_amount, category_id=category["id"]
            ),
        )

    builder.adjust(CATEGORIES_NUMBER_IN_ROW)

    return builder.as_markup()


def create_expense_manage_keyboard(expense_id: int, amount: Decimal) -> InlineKeyboardMarkup:
    """Create keyboard with manage options for the expense."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Удалить",
                    callback_data=ExpenseDeleteCallback(expense_id=expense_id).pack(),
                ),
                InlineKeyboardButton(
                    text="Валюта",
                    callback_data=ExpenseChangeCurrencyCallback(
                        expense_id=expense_id, amount=amount
                    ).pack(),
                ),
            ]
        ]
    )
