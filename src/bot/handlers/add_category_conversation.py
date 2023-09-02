import logging

from telegram import ReplyKeyboardRemove, Update
from telegram.ext import (CommandHandler, ContextTypes, ConversationHandler,
                          MessageHandler, filters)

from .main_handlers import cancel
from bot.constants.telegram_messages import (
    ENTER_CATEGORY_NAME,
    CATEGORY_ADD_SUCCESS,
    CATEGORY_ALREADY_EXISTS
)
from bot.api_requests import client, BadRequest

CONFIRMATION = 0


async def add_category(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Add category conversation entrypoint."""
    await update.message.reply_text(
        ENTER_CATEGORY_NAME,
        reply_markup=ReplyKeyboardRemove()
    )
    return CONFIRMATION


async def _category_confirmation(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    category_name = update.message.text.strip().title()
    try:
        response_data = await client.add_category(category_name)
        await update.message.reply_text(
            CATEGORY_ADD_SUCCESS.format(response_data['name'])
        )
        return ConversationHandler.END
    except BadRequest:
        await update.message.reply_html(
            CATEGORY_ALREADY_EXISTS.format(category_name)
        )
        return CONFIRMATION


add_category_handler = ConversationHandler(
    entry_points=[CommandHandler('add_category', add_category)],
    states={
        CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND,
                                      _category_confirmation)]
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)
