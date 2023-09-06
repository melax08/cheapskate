import datetime as dt

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from bot.api_requests import client
from bot.constants.telegram_messages import (MONEY_LEFT_MESSAGE,
                                             NO_TODAY_EXPENSES, TODAY_EXPENSES)
from bot.utils import auth

PSYCHOLOGICAL_EXPENSE_LIMIT: int = 100


@auth
async def get_money_left(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Sends the user message with money left from budget for current month."""
    response_data = await client.get_money_left()
    current_datetime = dt.datetime.fromisoformat(
        response_data['current_datetime']
    )
    current_month = current_datetime.strftime('%B')
    await update.message.reply_text(MONEY_LEFT_MESSAGE.format(
        current_month,
        response_data['budget'],
        response_data['money_spend'],
        response_data['money_left'])
    )


async def get_today_expenses(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Sends the user message with information about today expenses."""
    response_data = await client.get_today_expenses()
    today_expenses_amount = response_data['money_spend']
    if today_expenses_amount == 0:
        message = NO_TODAY_EXPENSES
    else:
        message = TODAY_EXPENSES.format(today_expenses_amount)

    if today_expenses_amount >= PSYCHOLOGICAL_EXPENSE_LIMIT:
        message += ' 🗿'

    await update.message.reply_text(message)


money_left_handler = CommandHandler('money_left', get_money_left)
today_handler = CommandHandler('today', get_today_expenses)
