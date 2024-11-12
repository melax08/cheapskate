import logging

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.constants import logging_messages, telegram_messages
from bot.constants.commands import CANCEL_COMMAND
from bot.utils import get_user_info

router = Router()


@router.message(CommandStart())
async def start_cmd(message: Message) -> None:
    """Show bot start message."""
    logging.info(
        logging_messages.START_BOT_LOG.format(get_user_info(message.from_user))
    )

    await message.answer(telegram_messages.START_MESSAGE)


@router.message(Command(CANCEL_COMMAND))
async def cancel_cmd(message: Message, state: FSMContext):
    """Cancel and end current user conversation."""
    await state.clear()
    await message.answer(
        text=telegram_messages.ACTION_CANCELED, reply_markup=ReplyKeyboardRemove()
    )
