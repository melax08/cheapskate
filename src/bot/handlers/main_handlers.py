import logging

from telegram import MenuButtonCommands, Update
from telegram.ext import CommandHandler, ContextTypes, ConversationHandler

from bot.constants.commands import COMMANDS
from bot.constants.logging_messages import START_BOT_LOG
from bot.constants.telegram_messages import ACTION_CANCELED, START_MESSAGE
from bot.utils import auth, get_user_info


@auth
async def start(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Occurs when someone starts the bot with /start command."""
    logging.info(START_BOT_LOG.format(get_user_info(update)))
    await context.bot.set_my_commands(commands=COMMANDS)
    await context.bot.set_chat_menu_button(
        menu_button=MenuButtonCommands()
    )
    await update.message.reply_html(
        START_MESSAGE.format(update.effective_user.mention_html())
    )


@auth
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    context.user_data.clear()
    await update.message.reply_text(ACTION_CANCELED)
    return ConversationHandler.END


start_handler = CommandHandler('start', start)
