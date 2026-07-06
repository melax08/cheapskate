from fastapi import APIRouter

from backend.app.api.endpoints.public import authorization_router
from configs.api_settings import PUBLIC_API_PATH

public_router = APIRouter(prefix=PUBLIC_API_PATH)

public_router.include_router(authorization_router, prefix="/authorization", tags=["authorization"])
