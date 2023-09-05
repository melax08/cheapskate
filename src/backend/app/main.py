from app.api.routers import main_router
from fastapi import FastAPI

from .core.config import settings

app = FastAPI(title=settings.app_title, description=settings.app_description)

app.include_router(main_router)
