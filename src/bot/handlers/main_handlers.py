import logging

from telegram import Update, MenuButtonCommands
from telegram.ext import ContextTypes, CommandHandler

from bot.constants.logging_messages import START_BOT_LOG
from bot.constants.telegram_messages import START_MESSAGE
from bot.utils import get_user_info
from bot.constants.commands import COMMANDS


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


start_handler = CommandHandler('start', start)
