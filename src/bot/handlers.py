from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler
)

from .messages import (
    WRONG_REQUEST,
    UPDATE_MESSAGE,
    CHOOSE_CATEGORY,
    DELETE_MESSAGE
)
from .validators import money_validator
from .api_requests import send_expense_to_api, delete_expense_request
from .constants import CATEGORIES, BUTTON_ROW_LEN
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


async def spending_money(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    try:
        money = money_validator(update.message.text)
    except ValueError:
        await update.message.reply_text(WRONG_REQUEST)
        return

    keyboard = await create_category_keyboard(money)

    await update.message.reply_text(
        CHOOSE_CATEGORY.format(money),
        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )


async def choose_category(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    money, category_id = query.data.split()
    money_left, expense_id = await send_expense_to_api(money, category_id)
    await query.answer()
    await query.edit_message_text(
        text=UPDATE_MESSAGE.format(
            money,
            CATEGORIES[int(category_id)],
            money_left
        ),
        reply_markup=InlineKeyboardMarkup.from_row(
            [InlineKeyboardButton('Удалить', callback_data=f'DEL {expense_id}')]
        )
    )


async def delete_expense(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    expense_to_delete_id = ''.join(query.data.split()[1:])
    await delete_expense_request(expense_to_delete_id)
    await query.answer()
    await query.edit_message_text(
        text=DELETE_MESSAGE
    )


spending_money_handler = MessageHandler(filters.TEXT, spending_money)
choose_category_handler = CallbackQueryHandler(choose_category)
delete_expense_handler = CallbackQueryHandler(
    delete_expense, pattern=r'DEL \d+'
)
