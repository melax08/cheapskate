import asyncio
import logging
from typing import Tuple

from telegram import Bot, Update
from telegram.constants import ParseMode

from bot.constants.constants import (ALLOWED_TELEGRAM_IDS, ECHO_MESSAGES,
                                     MONTH_NAME_MAP, TOKEN)
from bot.constants.logging_messages import ACCESS_DENIED_LOG
from bot.constants.telegram_messages import (ACCESS_DENIED,
                                             ANOTHER_USER_ACTION,
                                             CATEGORY_ITEM, MONEY_LEFT_HAS,
                                             MONEY_RAN_OUT)


def get_user_info(update: Update) -> str:
    """Creates a string with information about the current telegram user."""
    user = update.effective_user
    return f'{user.username}, {user.first_name} {user.last_name}, {user.id}'


def auth(func):
    """
    Decorator that can be used in telegram handlers.
    Allows access only to those telegram ids that are listed in the
    ALLOWED_TELEGRAM_IDS environment variable. If ALLOWED_TELEGRAM_IDS is
    empty, then allows access to all.
    """
    async def wrapper(*args, **kwargs):
        update = args[0]
        if (ALLOWED_TELEGRAM_IDS is not None
                and update.effective_user.id not in ALLOWED_TELEGRAM_IDS):
            logging.warning(ACCESS_DENIED_LOG.format(get_user_info(update)))
            await update.message.reply_html(ACCESS_DENIED)
            return
        return await func(*args, **kwargs)

    return wrapper


def money_left_calculate_message(
        money_left: str, first_message_part: str
) -> Tuple[float, str]:
    """Checks the money left value and generates a final message for the
    user."""
    money_left = float(money_left)
    if money_left >= 0:
        message = first_message_part + MONEY_LEFT_HAS
    else:
        money_left = abs(money_left)
        message = first_message_part + MONEY_RAN_OUT
    return money_left, message


def wrap_list_to_monospace(message_array: list) -> None:
    """
    Wraps the passed list with <code> </code> HTML tags.
    If you want telegram to correct parse this HTML tags, use:
    telegram.constants.ParseMode.HTML or update.message.reply_html shortcut.
    """
    if len(message_array) == 0:
        return
    message_array[0] = '<code>' + message_array[0]
    message_array[-1] = message_array[-1] + '</code>'


def append_categories_expenses_info(
        categories: list, message: list, category_label: str
) -> None:
    """Adds expenses information by categories to the message."""
    if categories:
        message.append(category_label)

        category_items = [
            CATEGORY_ITEM.format(category.get("name"), category.get("amount"))
            for category in categories
        ]

        wrap_list_to_monospace(category_items)
        message.extend(category_items)


def get_humanreadable_username(user: Update.effective_user) -> str:
    """
    Gets humanreadable information about specified telegram `effective_user`.
    Returns string of first_name + last_name,
    or username, if first_name and last_name is empty.
    """
    author_name_surname = [
        entry for entry in (user.first_name, user.last_name)
        if entry is not None
    ]
    if not author_name_surname:
        author_name_surname = [user.username]
    return ' '.join(author_name_surname)


async def reply_message_to_authorized_users(
        source_message: str, update: Update
) -> None:
    """Sends the information about the user action to another telegram users,
    whose telegram_id specified in the env variable `ALLOWED_TELEGRAM_IDS`"""
    if not ECHO_MESSAGES:
        return
    author = update.effective_user
    author_username = get_humanreadable_username(author)
    message_to_send = (
        ANOTHER_USER_ACTION.format(author_username, source_message)
    )

    authorized_ids_without_author = ALLOWED_TELEGRAM_IDS.copy()
    authorized_ids_without_author.remove(author.id)

    bot = Bot(token=TOKEN)

    await asyncio.gather(*[bot.send_message(
        telegram_id, message_to_send, parse_mode=ParseMode.HTML
    ) for telegram_id in authorized_ids_without_author])


def get_russian_month_name(month_name: str) -> str:
    """Returns the Russian name of the month."""
    return MONTH_NAME_MAP.get(month_name, month_name)
