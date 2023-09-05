from app.api.endpoints import category_router, expense_router
from fastapi import APIRouter

main_router = APIRouter(prefix='/api/v1')

main_router.include_router(
    category_router,
    prefix='/category',
    tags=['Category']
)

main_router.include_router(
    expense_router,
    prefix='/expense',
    tags=['Expense']
)
