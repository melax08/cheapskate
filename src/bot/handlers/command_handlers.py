import datetime as dt

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from bot.api_requests import get_api_client
from bot.constants.telegram_messages import (IN_CATEGORIES_LABEL,
                                             MONEY_LEFT_MESSAGE,
                                             MONTH_CATEGORIES_LABEL,
                                             NO_TODAY_EXPENSES, TODAY_EXPENSES,
                                             TOO_MUCH_MONEY_BRUH)
from bot.utils.utils import (append_categories_expenses_info, auth,
                             get_russian_month_name,
                             money_left_calculate_message)

PSYCHOLOGICAL_EXPENSE_LIMIT: int = 100


@auth
async def get_money_left(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Sends the user a message with information about the remaining funds for
     the current month and information about spending by categories."""
    async with get_api_client() as client:
        response_data = await client.get_money_left()

    current_datetime = dt.datetime.fromisoformat(
        response_data['current_datetime']
    )

    current_month = get_russian_month_name(current_datetime.strftime('%B'))

    money_left, message = money_left_calculate_message(
        response_data['money_left'],
        MONEY_LEFT_MESSAGE
    )

    message = [
        message.format(
            current_month,
            response_data['budget'],
            response_data['money_spent'],
            money_left
        )
    ]

    append_categories_expenses_info(
        response_data['categories'],
        message,
        MONTH_CATEGORIES_LABEL
    )

    await update.message.reply_html('\n'.join(message))


@auth
async def get_today_expenses(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Sends the user message with information about today expenses."""
    async with get_api_client() as client:
        response_data = await client.get_today_expenses()

    today_expenses_amount = response_data['money_spent']

    if today_expenses_amount == 0:
        await update.message.reply_text(NO_TODAY_EXPENSES)
        return

    message = [TODAY_EXPENSES.format(today_expenses_amount)]

    if today_expenses_amount >= PSYCHOLOGICAL_EXPENSE_LIMIT:
        message[0] += TOO_MUCH_MONEY_BRUH

    append_categories_expenses_info(
        response_data['categories'],
        message,
        IN_CATEGORIES_LABEL
    )

    await update.message.reply_html('\n'.join(message))


money_left_handler = CommandHandler('money_left', get_money_left)
today_handler = CommandHandler('today', get_today_expenses)
