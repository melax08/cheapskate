from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.cheapskate import get
from app.models import Category


async def check_category_exists(
        category_id: int, session: AsyncSession) -> Category:
    category = await get(Category, category_id, session)
    if category is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Category not found'
        )
    return category

