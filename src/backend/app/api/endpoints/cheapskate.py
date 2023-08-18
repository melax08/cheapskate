from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.cheapskate import Category, CategoryDB
from app.core.db import get_async_session

router = APIRouter()


@router.get('/category', response_model=list[CategoryDB])
async def get_all_categories(
        session: AsyncSession = Depends(get_async_session)
):
    """Gets the all expense categories."""
    ...
