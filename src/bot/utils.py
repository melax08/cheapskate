from telegram import InlineKeyboardButton, Update

from .constants import BUTTON_ROW_LEN
from .api_requests import client


async def create_category_keyboard(money: int) -> list:
    """Create keyboard with categories from API."""
    categories = await client.get_categories()

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
    info = update.message
    return (f'{info.chat.username}, {info.chat.first_name} '
            f'{info.chat.last_name}, {update.effective_user.id}')
