from aiogram import Router

from .add_expense import router as add_expense_router
from .delete_expense import router as delete_expense_router

router = Router()

router.include_routers(add_expense_router, delete_expense_router)
