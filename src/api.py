from fastapi import FastAPI

from backend.app.api.routers import main_router
from backend.app.core.config import settings

app = FastAPI(title=settings.app_title, description=settings.app_description)

app.include_router(main_router)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
