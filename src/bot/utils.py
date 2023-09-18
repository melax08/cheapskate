import logging
from typing import Tuple, Union

from telegram import InlineKeyboardButton, Update

from bot.constants.constants import ALLOWED_TELEGRAM_IDS, BUTTON_ROW_LEN
from bot.constants.logging_messages import ACCESS_DENIED_LOG
from bot.constants.telegram_messages import (ACCESS_DENIED, CATEGORY_ITEM,
                                             MONEY_LEFT_HAS, MONEY_RAN_OUT)

from .api_requests import get_api_client


async def create_category_keyboard(money: Union[float, int]) -> list:
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

    return keyboard


def get_user_info(update: Update) -> str:
    """Creates a string with information about the current telegram user."""
    user = update.effective_user
    return f'{user.username}, {user.first_name} {user.last_name}, {user.id}'


def auth(func):
    """
    Decorator that can be used in telegram handlers.
    Allows access only to those telegram ids that are listed in the
    ALLOWED_TELEGRAM_IDS environment variable. If ALLOWED_TELEGRAM_IDS is
    empty, then allows access to all.
    """
    async def wrapper(*args, **kwargs):
        update = args[0]
        if (ALLOWED_TELEGRAM_IDS is not None
                and update.effective_user.id not in ALLOWED_TELEGRAM_IDS):
            logging.warning(ACCESS_DENIED_LOG.format(get_user_info(update)))
            await update.message.reply_html(ACCESS_DENIED)
            return
        return await func(*args, **kwargs)

    return wrapper


def money_left_calculate_message(
        money_left: str, first_message_part: str
) -> Tuple[float, str]:
    """Checks the money left value and generates a final message for the
    user."""
    money_left = float(money_left)
    if money_left >= 0:
        message = first_message_part + MONEY_LEFT_HAS
    else:
        money_left = abs(money_left)
        message = first_message_part + MONEY_RAN_OUT
    return money_left, message


def wrap_list_to_monospace(message_array: list) -> None:
    """
    Wraps the passed list with <code> </code> HTML tags.
    If you want telegram to correct parse this HTML tags, use:
    telegram.constants.ParseMode.HTML or update.message.reply_html shortcut.
    """
    if len(message_array) == 0:
        return
    message_array[0] = '<code>' + message_array[0]
    message_array[-1] = message_array[-1] + '</code>'


def append_categories_expenses_info(
        categories: list, message: list, category_label: str
) -> None:
    """Adds expenses information by categories to the message."""
    if categories:
        message.append(category_label)

        category_items = [
            CATEGORY_ITEM.format(category.get("name"), category.get("amount"))
            for category in categories
        ]

        wrap_list_to_monospace(category_items)
        message.extend(category_items)
