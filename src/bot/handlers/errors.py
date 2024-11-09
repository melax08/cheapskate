import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import ErrorEvent, Message

from bot.constants import logging_messages, telegram_messages

router = Router()


# ToDo: fix it
@router.error()
async def error_handler(event: ErrorEvent, state: FSMContext, message: Message) -> None:
    """Handle all unhandled exceptions."""
    await state.clear()

    logging.critical(logging_messages.EXCEPTION_LOG, event.exception, exc_info=True)

    await message.answer(telegram_messages.API_ERROR)
