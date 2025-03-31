import asyncio
from decimal import Decimal

from aiogram import Bot
from aiogram.types import User

from bot.config import bot_settings
from bot.constants.constants import AMOUNT_DECIMAL_PLACES, MONTH_NAME_MAP
from bot.constants.telegram_messages import (
    ANOTHER_USER_ACTION,
    CATEGORY_ITEM,
    CURRENCY_STATISTIC_LABEL,
    MONEY_LEFT_HAS,
    MONEY_RAN_OUT,
)


def normalize_amount(amount: float | Decimal | str | int) -> Decimal:
    """
    Cast string, integer or float to decimal.
    Round a number to the desired number of decimal places.
    """
    return round(Decimal(amount), AMOUNT_DECIMAL_PLACES).normalize()


def get_user_info(user: User) -> str:
    """Creates a string with information about the current telegram user."""
    return f"{user.username}, {user.first_name} {user.last_name}, {user.id}"


def money_left_calculate_message(money_left: str, first_message_part: str) -> tuple[Decimal, str]:
    """Checks the money left value and generates a final message for the
    user."""
    money_left = normalize_amount(money_left)

    if money_left >= 0:
        message = first_message_part + MONEY_LEFT_HAS
    else:
        money_left = abs(money_left)
        message = first_message_part + MONEY_RAN_OUT

    return money_left, message


def wrap_list_to_monospace(message_array: list[str]) -> None:
    """
    Wraps the passed list with <code> </code> HTML tags.
    If you want telegram to correct parse this HTML tags, use:
    telegram.constants.ParseMode.HTML or update.message.reply_html shortcut.
    """
    if len(message_array) == 0:
        return
    message_array[0] = "<code>" + message_array[0]
    message_array[-1] = message_array[-1] + "</code>"


def append_currencies_categories_expenses_info(
    currencies: list, message: list, category_label: str | None = None
) -> None:
    """Adds expenses information by currencies and categories to the message."""
    if currencies:
        if category_label:
            message.append(category_label)

        for currency in currencies:
            currency_label = [
                CURRENCY_STATISTIC_LABEL.format(
                    currency["currency"]["name"],
                    currency["currency"]["letter_code"],
                    normalize_amount(currency["currency_amount"]),
                )
            ]

            category_items = [
                CATEGORY_ITEM.format(
                    category.get("name"), Decimal(category.get("amount")).normalize()
                )
                for category in currency["categories"]
            ]

            wrap_list_to_monospace(category_items)
            message.extend(currency_label + category_items)


def get_humanreadable_username(user: User) -> str:
    """
    Gets humanreadable information about specified telegram `effective_user`.
    Returns string of first_name + last_name,
    or username, if first_name and last_name is empty.
    """
    author_name_surname = [
        entry for entry in (user.first_name, user.last_name) if entry is not None
    ]
    if not author_name_surname:
        author_name_surname = [user.username]
    return " ".join(author_name_surname)


async def reply_message_to_authorized_users(source_message: str, user: User, bot: Bot) -> None:
    """Sends the information about the user action to another telegram users,
    whose telegram_id specified in the env variable `ALLOWED_TELEGRAM_IDS`"""
    if not bot_settings.echo_messages or not bot_settings.allowed_telegram_ids:
        return

    author_username = get_humanreadable_username(user)
    message_to_send = ANOTHER_USER_ACTION.format(author_username, source_message)

    authorized_ids_without_author = bot_settings.allowed_telegram_ids.copy()
    authorized_ids_without_author.remove(user.id)

    # ToDo: add except exception of aiogram errors (chat mute, nonexistent user, etc)
    await asyncio.gather(
        *[
            bot.send_message(telegram_id, message_to_send)
            for telegram_id in authorized_ids_without_author
        ]
    )


def get_russian_month_name(month_name: str) -> str:
    """Returns the Russian name of the month."""
    return MONTH_NAME_MAP.get(month_name, month_name)
