from telegram import InlineKeyboardButton, Update

from bot.constants.constants import BUTTON_ROW_LEN
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
