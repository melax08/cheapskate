from fastapi import APIRouter

from backend.app.api.endpoints import (
    category_router,
    currency_router,
    expense_router,
    report_router,
    setting_router,
    statistic_router,
)
from configs.api_settings import (
    API_PATH,
    CATEGORIES_PATH,
    CURRENCY_PATH,
    EXPENSE_PATH,
    REPORT_ROOT_PATH,
    SETTINGS_PATH,
    STATISTIC_ROOT_PATH,
)

main_router = APIRouter(prefix=API_PATH)


def __make_root_path(path: str) -> str:
    """Add a slash to the start of the string."""
    return "/" + path


main_router.include_router(
    category_router, prefix=__make_root_path(CATEGORIES_PATH), tags=["Category"]
)

main_router.include_router(expense_router, prefix=__make_root_path(EXPENSE_PATH), tags=["Expense"])

main_router.include_router(
    currency_router, prefix=__make_root_path(CURRENCY_PATH), tags=["Currency"]
)

main_router.include_router(
    setting_router, prefix=__make_root_path(SETTINGS_PATH), tags=["Settings"]
)

main_router.include_router(
    statistic_router, prefix=__make_root_path(STATISTIC_ROOT_PATH), tags=["Statistic"]
)

main_router.include_router(
    report_router, prefix=__make_root_path(REPORT_ROOT_PATH), tags=["Report"]
)
