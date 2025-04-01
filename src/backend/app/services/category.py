from backend.app.api.validators import check_category_name_duplicate
from backend.app.crud import category_crud
from backend.app.schemas.category import CategoryCreate, CategoryDB
from backend.app.services.base import BaseService


class CategoryService(BaseService):
    """Service to manage expense categories."""

    async def get_all_categories(self) -> list[CategoryDB]:
        """Get all expense categories."""
        return await category_crud.get_multi(self._session)

    async def create_category(self, category: CategoryCreate) -> CategoryDB:
        """Create expense category."""
        await check_category_name_duplicate(category.name, self._session)
        return await category_crud.create(category, self._session)
