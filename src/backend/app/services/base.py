from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.db import get_async_session


class BaseService:
    """Base service class with database session dependency injection."""

    def __init__(self, session: AsyncSession = Depends(get_async_session)) -> None:
        self._session = session
