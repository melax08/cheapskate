from aiogram import Router

from .add_currency import router as add_currency_router
from .change_currency import router as change_currency_router

router = Router()

router.include_routers(add_currency_router, change_currency_router)
