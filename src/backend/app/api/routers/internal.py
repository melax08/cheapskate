from fastapi import APIRouter

from backend.app.api.endpoints.internal import (
    category_router,
    currency_router,
    expense_router,
    report_router,
    setting_router,
    statistic_router,
    user_router,
)
from configs.api_settings import (
    CATEGORIES_PATH,
    CURRENCY_PATH,
    EXPENSE_PATH,
    INTERNAL_API_PATH,
    REPORT_ROOT_PATH,
    SETTINGS_PATH,
    STATISTIC_ROOT_PATH,
    USER_PATH,
)

internal_router = APIRouter(prefix=INTERNAL_API_PATH)


def __make_root_path(path: str) -> str:
    """Add a slash to the start of the string."""
    return "/" + path


internal_router.include_router(
    category_router, prefix=__make_root_path(CATEGORIES_PATH), tags=["Category"]
)
internal_router.include_router(
    expense_router, prefix=__make_root_path(EXPENSE_PATH), tags=["Expense"]
)
internal_router.include_router(
    currency_router, prefix=__make_root_path(CURRENCY_PATH), tags=["Currency"]
)
internal_router.include_router(
    setting_router, prefix=__make_root_path(SETTINGS_PATH), tags=["Settings"]
)
internal_router.include_router(
    statistic_router, prefix=__make_root_path(STATISTIC_ROOT_PATH), tags=["Statistic"]
)
internal_router.include_router(
    report_router, prefix=__make_root_path(REPORT_ROOT_PATH), tags=["Report"]
)
internal_router.include_router(user_router, prefix=__make_root_path(USER_PATH), tags=["User"])
