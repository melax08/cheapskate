from fastapi import APIRouter, Depends, status

from backend.app.dependencies.authorization import get_current_user
from backend.app.schemas.category import (
    CategoryCreate,
    CategoryDB,
    CategoryDBWithExpenses,
    CategoryUpdate,
)
from backend.app.services.category import CategoryService

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[CategoryDBWithExpenses])
async def categories_list(
    category_service: CategoryService = Depends(CategoryService),
) -> list[CategoryDBWithExpenses]:
    return await category_service.get_categories_with_expenses_count()


@router.get("/{category_id}", response_model=CategoryDB)
async def categories_detail(
    category_id: int,
    category_service: CategoryService = Depends(CategoryService),
) -> CategoryDB:
    return await category_service.get_category_by_id(category_id)


@router.post("", response_model=CategoryDB, status_code=status.HTTP_201_CREATED)
async def categories_create(
    category: CategoryCreate,
    category_service: CategoryService = Depends(CategoryService),
) -> CategoryDB:
    return await category_service.create_category(category)


@router.patch("/{category_id}", response_model=CategoryDB)
async def categories_partial_update(
    category_id: int,
    category: CategoryUpdate,
    category_service: CategoryService = Depends(CategoryService),
) -> CategoryDB:
    return await category_service.update_category(category_id, category)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def categories_delete(
    category_id: int,
    category_service: CategoryService = Depends(CategoryService),
) -> None:
    await category_service.delete_category(category_id)
