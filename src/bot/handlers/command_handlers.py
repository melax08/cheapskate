import datetime as dt

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from bot.api_requests import get_api_client
from bot.constants.telegram_messages import (CATEGORY_ITEM,
                                             IN_CATEGORIES_LABEL,
                                             MONEY_LEFT_MESSAGE,
                                             NO_TODAY_EXPENSES, TODAY_EXPENSES,
                                             TOO_MUCH_MONEY_BRUH)
from bot.utils import (auth, money_left_calculate_message,
                       wrap_list_to_monospace)

PSYCHOLOGICAL_EXPENSE_LIMIT: int = 100


@auth
async def get_money_left(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Sends the user message with money left from budget for current month."""
    async with get_api_client() as client:
        response_data = await client.get_money_left()

    current_datetime = dt.datetime.fromisoformat(
        response_data['current_datetime']
    )
    current_month = current_datetime.strftime('%B')

    money_left, message = money_left_calculate_message(
        response_data['money_left'],
        MONEY_LEFT_MESSAGE
    )

    await update.message.reply_text(message.format(
        current_month,
        response_data['budget'],
        response_data['money_spend'],
        money_left)
    )


@auth
async def get_today_expenses(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Sends the user message with information about today expenses."""

    async with get_api_client() as client:
        response_data = await client.get_today_expenses()

    today_expenses_amount = response_data['money_spend']

    if today_expenses_amount == 0:
        await update.message.reply_text(NO_TODAY_EXPENSES)
        return

    message = [TODAY_EXPENSES.format(today_expenses_amount)]

    if today_expenses_amount >= PSYCHOLOGICAL_EXPENSE_LIMIT:
        message[0] += TOO_MUCH_MONEY_BRUH

    categories = response_data['categories']
    message.append(IN_CATEGORIES_LABEL)

    category_items = [
        CATEGORY_ITEM.format(category.get("name"), category.get("amount"))
        for category in categories
    ]

    wrap_list_to_monospace(category_items)
    message.extend(category_items)

    await update.message.reply_html('\n'.join(message))


money_left_handler = CommandHandler('money_left', get_money_left)
today_handler = CommandHandler('today', get_today_expenses)
