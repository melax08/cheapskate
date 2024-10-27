import logging

from bot.config import bot_settings
from bot.constants.logging_messages import ACCESS_DENIED_LOG
from bot.constants.telegram_messages import ACCESS_DENIED
from bot.utils.utils import get_user_info


# ToDo: move logic of auth to middleware
def auth(func):
    """
    Decorator that can be used in telegram handlers.
    Allows access only to those telegram ids that are listed in the
    ALLOWED_TELEGRAM_IDS environment variable. If ALLOWED_TELEGRAM_IDS is
    empty, then allows access to all.
    """

    async def wrapper(*args, **kwargs):
        update = args[0]

        if (
            bot_settings.allowed_telegram_ids
            and update.effective_user.id not in bot_settings.allowed_telegram_ids
        ):
            logging.warning(ACCESS_DENIED_LOG.format(get_user_info(update)))
            await update.message.reply_html(ACCESS_DENIED)
            return

        return await func(*args, **kwargs)

    return wrapper
