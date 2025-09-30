import logging
from time import time

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import CallbackQuery, Message

from bot.api_requests import APIClient
from bot.callbacks.report import ReportUpdateCallback
from bot.constants import logging_messages
from bot.constants.commands import REPORT_COMMAND
from bot.keyboards.report import report_markup
from bot.utils import get_user_info

router = Router()


@router.message(StateFilter(None), Command(REPORT_COMMAND))
async def get_report_cmd(message: Message, client: APIClient) -> None:
    report = await client.get_report()
    await message.answer(report.get_message(), reply_markup=report_markup)


@router.callback_query(ReportUpdateCallback.filter())
async def update_report(callback: CallbackQuery, client: APIClient) -> None:
    time_before_start = time()

    report = await client.update_report()
    await callback.message.edit_text(text=report.get_message(), reply_markup=report_markup)
    await callback.answer()

    logging.info(
        logging_messages.UPDATE_REPORT_LOG.format(
            user=get_user_info(callback.from_user), time_spent=time() - time_before_start
        )
    )
