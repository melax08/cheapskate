import datetime as dt
from decimal import Decimal

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from bot.api_requests import get_api_client
from bot.constants.telegram_messages import (
    MONEY_LEFT_MESSAGE,
    MONTH_CATEGORIES_LABEL,
    NO_TODAY_EXPENSES,
    TODAY_EXPENSES,
)
from bot.decorators import auth
from bot.utils.utils import (
    append_currencies_categories_expenses_info,
    get_russian_month_name,
    money_left_calculate_message,
)

# ToDo: refactor this or remove
# PSYCHOLOGICAL_EXPENSE_LIMIT: int = 100


@auth
async def get_money_left(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends the user a message with information about the remaining funds for
    the current month and information about spending by categories."""
    async with get_api_client() as client:
        response_data = await client.get_money_left()

    current_datetime = dt.datetime.fromisoformat(response_data["current_datetime"])

    current_month = get_russian_month_name(current_datetime.strftime("%B"))

    money_left, message = money_left_calculate_message(
        response_data["money_left"], MONEY_LEFT_MESSAGE
    )

    message = [
        message.format(
            current_month,
            Decimal(response_data["budget"]).normalize(),
            Decimal(response_data["money_spent"]).normalize(),
            money_left,
            currency_code=response_data["default_currency"]["letter_code"],
        )
    ]

    append_currencies_categories_expenses_info(
        response_data["currencies"], message, MONTH_CATEGORIES_LABEL
    )

    await update.message.reply_html("\n".join(message))


@auth
async def get_today_expenses(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Sends the user message with information about today expenses."""
    async with get_api_client() as client:
        response_data = await client.get_today_expenses()

    currencies = response_data["currencies"]

    if not currencies:
        await update.message.reply_text(NO_TODAY_EXPENSES)
    else:
        message = [TODAY_EXPENSES]

        append_currencies_categories_expenses_info(currencies, message)

        await update.message.reply_html("\n".join(message))


money_left_handler = CommandHandler("money_left", get_money_left)
today_handler = CommandHandler("today", get_today_expenses)
