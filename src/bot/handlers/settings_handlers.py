from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from bot.api_requests import get_api_client
from bot.constants.telegram_messages import SETTINGS_INFO
from bot.utils.keyboards import settings_markup


async def get_settings_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Command to get information about current application settings."""
    async with get_api_client() as client:
        response_data = await client.get_settings()
        currency_data = response_data.get("default_currency")

    await update.message.reply_html(
        SETTINGS_INFO.format(
            currency_data.get("name"),
            currency_data.get("letter_code"),
            response_data.get("budget"),
        ),
        reply_markup=settings_markup,
    )


settings_handler = CommandHandler("settings", get_settings_handler)
