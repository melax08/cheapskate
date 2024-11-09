from aiogram import Router

from .month import router as month_router
from .period import router as period_router
from .today import router as today_router

router = Router()

router.include_routers(today_router, month_router, period_router)
