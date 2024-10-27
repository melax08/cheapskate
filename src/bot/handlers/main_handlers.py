import logging

from telegram import MenuButtonCommands, Update
from telegram.ext import CommandHandler, ContextTypes, ConversationHandler

from bot.constants.commands import COMMANDS
from bot.constants.logging_messages import EXCEPTION_LOG, START_BOT_LOG
from bot.constants.telegram_messages import ACTION_CANCELED, API_ERROR, START_MESSAGE
from bot.decorators import auth
from bot.utils.utils import get_user_info


@auth
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Occurs when someone starts the bot with /start command."""
    logging.info(START_BOT_LOG.format(get_user_info(update)))
    # ToDo: move to on startup function
    await context.bot.set_my_commands(commands=COMMANDS)
    await context.bot.set_chat_menu_button(menu_button=MenuButtonCommands())
    # end ToDo
    await update.message.reply_html(
        START_MESSAGE.format(update.effective_user.mention_html())
    )


@auth
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    context.user_data.clear()
    await update.message.reply_text(ACTION_CANCELED)
    return ConversationHandler.END


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the current user
    about the problem."""
    logging.error(EXCEPTION_LOG, exc_info=context.error)
    if update is not None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=API_ERROR)


start_handler = CommandHandler("start", start)
