from fastapi import FastAPI

from backend.app.api.routers import internal_router, public_router
from backend.app.core.config import settings

app = FastAPI(title=settings.app_title, description=settings.app_description)

app.include_router(internal_router)
app.include_router(public_router)
