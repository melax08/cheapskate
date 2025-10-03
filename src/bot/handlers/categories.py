import logging

from aiogram import Bot, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.api_requests import APIClient
from bot.constants import logging_messages, telegram_messages
from bot.constants.commands import ADD_CATEGORY_COMMAND
from bot.exceptions import APIError
from bot.states.categories import AddCategoryState
from bot.utils import get_user_info, reply_message_to_authorized_users
from bot.validators import category_name_validator
from configs.enums import APIErrorCode

router = Router()


@router.message(StateFilter(None), Command(ADD_CATEGORY_COMMAND))
async def add_category_cmd(message: Message, state: FSMContext) -> None:
    """Add category conversation entrypoint."""
    await message.answer(text=telegram_messages.ENTER_CATEGORY_NAME)
    await state.set_state(AddCategoryState.writing_category_name)


# ToDo: no commands (only messages accept)
@router.message(AddCategoryState.writing_category_name)
async def add_category_name_chosen(
    message: Message, state: FSMContext, client: APIClient, bot: Bot
) -> None:
    """Validate entered category name and send new category to API."""
    category_name = message.text.strip().title()

    try:
        category_name_validator(category_name)

        response_data = await client.add_category(category_name)

        logging.info(
            logging_messages.ADDED_CATEGORY_LOG.format(
                get_user_info(message.from_user), category_name
            )
        )

        message_to_send = telegram_messages.CATEGORY_ADD_SUCCESS.format(response_data["name"])
        await message.answer(message_to_send)
        await state.clear()
        await reply_message_to_authorized_users(message_to_send, message.from_user, bot)

    except APIError as error:
        if error.error_code == APIErrorCode.CATEGORY_EXISTS:
            logging.warning(
                logging_messages.CATEGORY_ALREADY_EXISTS_LOG.format(
                    get_user_info(message.from_user), category_name
                )
            )
            await message.answer(telegram_messages.CATEGORY_ALREADY_EXISTS.format(category_name))
        else:
            raise
    except ValueError:
        logging.warning(
            logging_messages.CATEGORY_NAME_TOO_LONG_LOG.format(
                get_user_info(message.from_user), category_name
            )
        )
        await message.answer(telegram_messages.CATEGORY_NAME_TOO_LONG)
