from fastapi import HTTPException, status

from backend.app.api.validators import check_category_exists, check_category_name_duplicate
from backend.app.crud import category_crud
from backend.app.models.category import Category
from backend.app.schemas.category import CategoryCreate, CategoryDBWithExpenses
from backend.app.services.base import BaseService


class CategoryService(BaseService):
    """Service to manage expense categories."""

    async def get_category_by_id(self, category_id: int) -> Category:
        return await check_category_exists(category_id, self._session)

    async def get_all_categories(self, only_visible: bool = False) -> list[Category]:
        """Get all expense categories."""
        return await category_crud.get_all_categories(only_visible, self._session)

    async def get_categories_with_expenses_count(self) -> list[CategoryDBWithExpenses]:
        categories_data = await category_crud.get_all_categories_with_expenses_count(self._session)
        return [
            CategoryDBWithExpenses(
                name=category.name,
                is_visible=category.is_visible,
                id=category.id,
                expenses_count=expenses_count,
            )
            for category, expenses_count in categories_data
        ]

    async def create_category(self, category: CategoryCreate) -> Category:
        """Create expense category."""
        await check_category_name_duplicate(category.name, self._session)
        return await category_crud.create(category, self._session)

    async def update_category(self, category_id: int, category_data: CategoryCreate) -> Category:
        category_to_update = await check_category_exists(category_id, self._session)
        if category_data.name is not None and category_data.name != category_to_update.name:
            await check_category_name_duplicate(category_data.name, self._session)
        return await category_crud.update(category_to_update, category_data, self._session)

    async def delete_category(self, category_id: int) -> Category:
        """User can delete category with no expenses."""
        category_to_delete = await check_category_exists(category_id, self._session)

        if await category_crud.is_category_has_expenses(category_to_delete, self._session):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Нельзя удалить категорию с тратами"
            )

        return await category_crud.remove(category_to_delete, self._session)
