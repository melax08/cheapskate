from fastapi import APIRouter

from backend.app.api.endpoints import category_router, expense_router, currency_router
from utils.api_settings import API_PATH, CATEGORIES_PATH, EXPENSE_PATH, CURRENCY_PATH

main_router = APIRouter(prefix=API_PATH)


def __make_root_path(path: str) -> str:
    """Add a slash to the start of the string."""
    return '/' + path


main_router.include_router(
    category_router,
    prefix=__make_root_path(CATEGORIES_PATH),
    tags=['Category']
)

main_router.include_router(
    expense_router,
    prefix=__make_root_path(EXPENSE_PATH),
    tags=['Expense']
)

main_router.include_router(
    currency_router,
    prefix=__make_root_path(CURRENCY_PATH),
    tags=['Currency']
)
