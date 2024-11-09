from aiogram import Router

from .add_currency import router as add_currency_router

router = Router()

router.include_routers(add_currency_router)
