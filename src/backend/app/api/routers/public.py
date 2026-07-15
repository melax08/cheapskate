from fastapi import APIRouter

from backend.app.api.endpoints.public import (
    authorization_router,
    category_router,
    currency_router,
    setting_router,
)
from configs.api_settings import PUBLIC_API_PATH

public_router = APIRouter(prefix=PUBLIC_API_PATH)

public_router.include_router(authorization_router, prefix="/authorization", tags=["authorization"])
public_router.include_router(category_router, prefix="/categories", tags=["category"])
public_router.include_router(currency_router, prefix="/currencies", tags=["currency"])
public_router.include_router(setting_router, prefix="/settings", tags=["settings"])
