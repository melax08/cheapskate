import logging
from decimal import Decimal, InvalidOperation

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot.api_requests import get_api_client
from bot.constants.logging_messages import (
    SET_NEW_BUDGET_LOG,
    WRONG_BUDGET_LOG,
)
from bot.constants.telegram_messages import (
    ENTER_NEW_BUDGET,
    NEW_BUDGET_SET_SUCCESS,
    WRONG_NEW_BUDGET,
)
from bot.decorators import auth
from bot.handlers.main_handlers import cancel
from bot.utils.keyboards import settings_markup
from bot.utils.utils import get_user_info, reply_message_to_authorized_users

# @auth
# async def get_settings_handler(
#     update: Update, context: ContextTypes.DEFAULT_TYPE
# ) -> None:
#     """Command to get information about current application settings."""
#     async with get_api_client() as client:
#         settings = await client.get_settings()
#
#     await update.message.reply_html(
#         settings.get_settings_message(),
#         reply_markup=settings_markup,
#     )


# @auth
# async def change_default_currency(
#     update: Update, context: ContextTypes.DEFAULT_TYPE
# ) -> None:
#     """Show the list of available currencies to set as default currency."""
#     query = update.callback_query
#
#     try:
#         currency_keyboard = await select_default_currency_keyboard()
#     except ValueError:
#         logging.warning(NO_CURRENCIES_LOG.format(get_user_info(update)))
#         await query.edit_message_text(text=NO_CURRENCIES, reply_markup=None)
#         return
#
#     await query.edit_message_text(
#         text=SELECT_NEW_DEFAULT_CURRENCY,
#         reply_markup=currency_keyboard,
#     )


# @auth
# async def set_default_currency(
#     update: Update, context: ContextTypes.DEFAULT_TYPE
# ) -> None:
#     """Set the new default currency for future expenses in the application."""
#     query = update.callback_query
#     _, currency_id = query.data.split()
#
#     async with get_api_client() as client:
#         try:
#             settings = await client.set_default_currency(int(currency_id))
#         except APIError:
#             logging.warning(
#                 WRONG_CURRENCY_LOG.format(get_user_info(update), currency_id)
#             )
#             currency_keyboard = await select_default_currency_keyboard()
#             await query.edit_message_text(
#                 text=NONEXISTENT_CURRENCY,
#                 reply_markup=currency_keyboard,
#             )
#             return
#
#     await query.answer()
#     logging.info(
#         SET_NEW_DEFAULT_CURRENCY_LOG.format(
#             get_user_info(update), settings.currency_name
#         )
#     )
#     await query.edit_message_text(
#         text=settings.get_settings_message_with_info(NEW_DEFAULT_CURRENCY_SET_SUCCESS),
#         reply_markup=settings_markup,
#         parse_mode=ParseMode.HTML,
#     )
#     await reply_message_to_authorized_users(
#         (
#             f"{NEW_DEFAULT_CURRENCY_SET_SUCCESS} {settings.currency_name} "
#             f"({settings.currency_code})"
#         ),
#         update,
#     )


_CONFIRMATION = 0


@auth
async def change_budget(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Change the month budget of expenses in application."""
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text=ENTER_NEW_BUDGET,
        parse_mode=ParseMode.HTML,
    )
    return _CONFIRMATION


@auth
async def _budget_confirmation(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Confirm changing of month budget of expenses in application."""
    new_budget = update.message.text.strip()

    try:
        async with get_api_client() as client:
            settings = await client.set_budget(Decimal(new_budget))

        await update.message.reply_html(
            settings.get_settings_message_with_info(NEW_BUDGET_SET_SUCCESS),
            reply_markup=settings_markup,
        )
        await reply_message_to_authorized_users(
            source_message=f"{NEW_BUDGET_SET_SUCCESS} {settings.budget}", update=update
        )

        logging.info(SET_NEW_BUDGET_LOG.format(get_user_info(update), new_budget))
        return ConversationHandler.END
    except (ValueError, InvalidOperation):
        logging.warning(WRONG_BUDGET_LOG.format(get_user_info(update), new_budget))
        await update.message.reply_html(WRONG_NEW_BUDGET)
        return _CONFIRMATION


settings_handler = CommandHandler("settings", get_settings_handler)
change_default_currency_handler = CallbackQueryHandler(
    change_default_currency, pattern="change_currency"
)
set_default_currency_handler = CallbackQueryHandler(
    set_default_currency, pattern=r"DEFAULT_CUR \d+"
)
set_budget_handler = ConversationHandler(
    # ToDo: refactor this
    entry_points=[CallbackQueryHandler(change_budget, pattern="change_budget")],
    states={
        _CONFIRMATION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, _budget_confirmation)
        ]
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
