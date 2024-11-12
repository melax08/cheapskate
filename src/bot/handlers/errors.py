import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import ErrorEvent, Message

from bot.constants import logging_messages, telegram_messages

router = Router()


@router.error()
async def error_handler(event: ErrorEvent, state: FSMContext) -> None:
    """Handle all unhandled exceptions."""
    await state.clear()

    logging.critical(logging_messages.EXCEPTION_LOG, event.exception, exc_info=True)

    message: Message = event.update.message or event.update.callback_query.message
    await message.answer(telegram_messages.API_ERROR)
