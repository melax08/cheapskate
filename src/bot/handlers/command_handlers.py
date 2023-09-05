from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from bot.api_requests import client
from bot.constants.telegram_messages import MONEY_LEFT_MESSAGE
from bot.utils import auth


@auth
async def get_money_left(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Sends the user message with money left from budget for current month."""
    response_data = await client.get_money_left()
    await update.message.reply_text(MONEY_LEFT_MESSAGE.format(
        response_data['budget'], response_data['money_left'])
    )


money_left_handler = CommandHandler('money_left', get_money_left)
