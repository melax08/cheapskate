import logging

from telegram import ReplyKeyboardRemove, Update
from telegram.ext import (CommandHandler, ContextTypes, ConversationHandler,
                          MessageHandler, filters)

from bot.api_requests import BadRequest, get_api_client
from bot.constants.logging_messages import (ADDED_CATEGORY_LOG,
                                            CATEGORY_ALREADY_EXISTS_LOG)
from bot.constants.telegram_messages import (CATEGORY_ADD_SUCCESS,
                                             CATEGORY_ALREADY_EXISTS,
                                             ENTER_CATEGORY_NAME)
from bot.utils import auth, get_user_info

from .main_handlers import cancel

CONFIRMATION = 0


@auth
async def add_category(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Add category conversation entrypoint."""
    await update.message.reply_text(
        ENTER_CATEGORY_NAME,
        reply_markup=ReplyKeyboardRemove()
    )
    return CONFIRMATION


@auth
async def _category_confirmation(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    category_name = update.message.text.strip().title()
    try:
        async with get_api_client() as client:
            response_data = await client.add_category(category_name)

        logging.info(ADDED_CATEGORY_LOG.format(
            get_user_info(update),
            category_name)
        )
        await update.message.reply_text(
            CATEGORY_ADD_SUCCESS.format(response_data['name'])
        )
        return ConversationHandler.END
    except BadRequest:
        logging.warning(CATEGORY_ALREADY_EXISTS_LOG.format(
            get_user_info(update),
            category_name)
        )
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
