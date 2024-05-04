from backend.app.api.routers import main_router
from backend.app.core.config import settings
from fastapi import FastAPI

app = FastAPI(title=settings.app_title, description=settings.app_description)

app.include_router(main_router)
