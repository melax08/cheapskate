import logging

from aiogram import Bot, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from configs.constants import COUNTRY_LENGTH, MAX_CURRENCY_NAME_LENGTH

from bot.api_requests import APIClient, BadRequest
from bot.constants import logging_messages, telegram_messages
from bot.constants.commands import ADD_CURRENCY_COMMAND
from bot.states.currencies import AddCurrency
from bot.utils.utils import get_user_info, reply_message_to_authorized_users
from bot.utils.validators import (
    currency_code_validator,
    currency_country_validator,
    currency_name_validator,
)

router = Router()


@router.message(StateFilter(None), Command(ADD_CURRENCY_COMMAND))
async def add_currency_cmd(message: Message, state: FSMContext) -> None:
    """Start add currency conversation handler."""
    await message.answer(text=telegram_messages.ENTER_CURRENCY_NAME)
    await state.set_state(AddCurrency.entering_currency_name)


@router.message(AddCurrency.entering_currency_name)
async def add_currency_name_chosen(message: Message, state: FSMContext) -> None:
    """Confirm currency name and ask user to write currency code."""
    currency_name = message.text.strip()

    try:
        currency_name_validator(currency_name)

        await state.update_data(currency_name=currency_name)
        await message.answer(telegram_messages.ENTER_CURRENCY_CODE)
        await state.set_state(AddCurrency.entering_currency_code)

    except ValueError:
        logging.warning(
            logging_messages.CURRENCY_NAME_TOO_LONG_LOG.format(
                get_user_info(message.from_user), currency_name
            )
        )
        await message.answer(
            telegram_messages.VALIDATION_ERROR_CURRENCY_NAME.format(
                MAX_CURRENCY_NAME_LENGTH
            )
        )


@router.message(AddCurrency.entering_currency_code)
async def add_currency_code_chosen(message: Message, state: FSMContext) -> None:
    """Confirm currency letter code and ask user to write currency country."""
    currency_code = message.text.strip().upper()

    try:
        currency_code_validator(currency_code)

        await state.update_data(currency_letter_code=currency_code)
        await message.answer(telegram_messages.ENTER_CURRENCY_COUNTRY)
        await state.set_state(AddCurrency.entering_currency_country)

    except ValueError:
        logging.warning(
            logging_messages.CURRENCY_INCORRECT_CODE_LOG.format(
                get_user_info(message.from_user), currency_code
            )
        )
        await message.answer(telegram_messages.VALIDATION_ERROR_CURRENCY_CODE)


@router.message(AddCurrency.entering_currency_country)
async def add_currency_country_chosen(
    message: Message, state: FSMContext, client: APIClient, bot: Bot
) -> None:
    """Confirm country name and send all collected data to the API."""
    country_name = message.text.strip()

    try:
        currency_country_validator(country_name)

        user_data = await state.get_data()

        response_data = await client.add_currency(
            name=user_data.get("currency_name"),
            letter_code=user_data.get("currency_letter_code"),
            country=country_name,
        )

        message_to_send = telegram_messages.CURRENCY_ADD_SUCCESS.format(
            response_data.get("name"),
            response_data.get("letter_code"),
            response_data.get("country"),
        )

        logging.info(
            logging_messages.CURRENCY_ADDED_NEW_LOG.format(
                get_user_info(message.from_user), response_data.get("name")
            )
        )
        await message.answer(message_to_send)
        await state.clear()
        await reply_message_to_authorized_users(message_to_send, message.from_user, bot)

    except BadRequest:
        logging.warning(
            logging_messages.CURRENCY_NOT_UNIQUE_LOG.format(
                get_user_info(message.from_user)
            )
        )
        await message.answer(telegram_messages.CURRENCY_NOT_UNIQUE)
        await state.clear()
    except ValueError:
        logging.warning(
            logging_messages.CURRENCY_COUNTRY_TOO_LONG_LOG.format(
                get_user_info(message.from_user), country_name
            )
        )
        await message.answer(
            telegram_messages.VALIDATION_ERROR_COUNTRY.format(COUNTRY_LENGTH)
        )
