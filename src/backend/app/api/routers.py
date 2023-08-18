from fastapi import APIRouter

from app.api.endpoints import cheapskate_router

main_router = APIRouter()
main_router.include_router(
    cheapskate_router,
    prefix='/api/v1',
    tags=['Money control']
)
