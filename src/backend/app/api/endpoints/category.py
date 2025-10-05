from fastapi import APIRouter, Depends

from backend.app.schemas.category import CategoryCreate, CategoryDB
from backend.app.services.category import CategoryService

router = APIRouter()


@router.get("/", response_model=list[CategoryDB])
async def get_all_categories(
    only_visible: bool = False,
    category_service: CategoryService = Depends(CategoryService),
) -> list[CategoryDB]:
    """Get all expense categories."""
    return await category_service.get_all_categories(only_visible)


@router.post("/", response_model=CategoryDB)
async def create_category(
    category: CategoryCreate, category_service: CategoryService = Depends(CategoryService)
) -> CategoryDB:
    """Create expense category."""
    return await category_service.create_category(category)
