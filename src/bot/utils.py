import logging

from telegram import InlineKeyboardButton, Update

from bot.constants.constants import ALLOWED_TELEGRAM_IDS, BUTTON_ROW_LEN
from bot.constants.logging_messages import ACCESS_DENIED_LOG
from bot.constants.telegram_messages import ACCESS_DENIED

from .api_requests import client


async def create_category_keyboard(money: int) -> list:
    """Create keyboard with categories from API."""
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
