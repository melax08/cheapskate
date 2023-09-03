from telegram import Update
from telegram.ext import (ContextTypes, CommandHandler)

from bot.api_requests import client
from bot.constants.telegram_messages import MONEY_LEFT_MESSAGE


async def get_money_left(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Sends the user message with money left from budget for current month."""
    response_data = await client.get_money_left()
    await update.message.reply_text(MONEY_LEFT_MESSAGE.format(
        response_data['budget'], response_data['money_left'])
    )


money_left_handler = CommandHandler('money_left', get_money_left)
