from fastapi import APIRouter

from configs.api_settings import PUBLIC_API_PATH

public_router = APIRouter(prefix=PUBLIC_API_PATH)
