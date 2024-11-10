from aiogram import Router

from .change_default_currency import router as change_default_currency_router
from .get_settings import router as get_settings_router

router = Router()

router.include_routers(get_settings_router, change_default_currency_router)
