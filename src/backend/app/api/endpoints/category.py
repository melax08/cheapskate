from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.validators import check_category_name_duplicate
from backend.app.core.db import get_async_session
from backend.app.crud import category_crud
from backend.app.schemas.category import CategoryCreate, CategoryDB

router = APIRouter()


@router.get('/', response_model=list[CategoryDB])
async def get_all_categories(
        session: AsyncSession = Depends(get_async_session)
):
    """Gets the all expense categories."""
    categories = await category_crud.get_multi(session)
    return categories


@router.post('/', response_model=CategoryDB)
async def create_category(
        category: CategoryCreate,
        session: AsyncSession = Depends(get_async_session)
):
    await check_category_name_duplicate(category.name, session)
    new_category = await category_crud.create(category, session)
    return new_category
