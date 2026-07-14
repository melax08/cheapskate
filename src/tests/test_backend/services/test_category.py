import pytest
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.category import Category
from backend.app.models.expense import Expense
from backend.app.schemas.category import CategoryCreate, CategoryUpdate
from backend.app.services.category import CategoryService
from tests.test_backend.factories.category import CategoryFactory
from tests.test_backend.factories.expense import ExpenseFactory


@pytest.mark.anyio
class TestCategoryService:
    async def test_get_existed_category_by_id(
        self, category_service: CategoryService, category: Category
    ) -> None:
        category_db = await category_service.get_category_by_id(category.id)
        assert category_db is category

    async def test_get_unexisted_category_by_id(self, category_service: CategoryService) -> None:
        unexisted_category_id = 123
        with pytest.raises(HTTPException, match="Категория не найдена"):
            await category_service.get_category_by_id(unexisted_category_id)

    async def test_get_all_categories(
        self, category_service: CategoryService, db_session: AsyncSession
    ) -> None:
        visible_categories_count = 7
        hidden_categories_count = 3

        visible_categories = await CategoryFactory.create_batch_async(
            db_session, size=visible_categories_count, is_visible=True
        )
        await CategoryFactory.create_batch_async(
            db_session, size=hidden_categories_count, is_visible=False
        )

        all_categories = await category_service.get_all_categories(only_visible=False)
        assert len(all_categories) == visible_categories_count + hidden_categories_count

        only_visible_categories = await category_service.get_all_categories(only_visible=True)
        assert only_visible_categories == visible_categories

    async def test_categories_with_expenses_count(
        self, db_session: AsyncSession, category_service: CategoryService
    ) -> None:
        category_with_expenses = await CategoryFactory.create_async(db_session)
        await CategoryFactory.create_async(db_session)
        expected_expenses_count = 4
        await ExpenseFactory.create_batch_async(
            session=db_session, size=expected_expenses_count, category=category_with_expenses
        )

        categories_with_expenses_count = await category_service.get_categories_with_expenses_count()
        for category in categories_with_expenses_count:
            if category.id == category_with_expenses.id:
                assert category.expenses_count == expected_expenses_count
            else:
                assert category.expenses_count == 0

    async def test_create_category(self, category_service: CategoryService) -> None:
        category_name = "test"
        category = await category_service.create_category(
            CategoryCreate(
                name=category_name,
                is_visible=True,
            )
        )
        assert category.id is not None
        assert category.name == category_name
        assert category.is_visible

    async def test_create_category_with_duplicate_name(
        self, category_service: CategoryService, category: Category, db_session: AsyncSession
    ) -> None:
        with pytest.raises(HTTPException, match="Категория с таким названием уже существует"):
            await category_service.create_category(
                CategoryCreate(
                    name=category.name,
                    is_visible=True,
                )
            )

        categories_count = await db_session.execute(
            select(func.count()).where(Category.name == category.name)
        )
        assert categories_count.scalars().first() == 1

    async def test_update_nonexisted_category(self, category_service: CategoryService) -> None:
        unexisted_category_id = 123
        with pytest.raises(HTTPException, match="Категория не найдена"):
            await category_service.update_category(
                unexisted_category_id, CategoryUpdate(name="test")
            )

    async def test_update_category_with_duplicate_name(
        self, category_service: CategoryService, db_session: AsyncSession
    ) -> None:
        first_category = await CategoryFactory.create_async(db_session)
        first_category_name = first_category.name
        second_category = await CategoryFactory.create_async(db_session)

        with pytest.raises(HTTPException, match="Категория с таким названием уже существует"):
            await category_service.update_category(
                first_category.id, CategoryUpdate(name=second_category.name)
            )

        await db_session.refresh(first_category)
        assert first_category.name == first_category_name

    async def test_update_category(
        self, category_service: CategoryService, category: Category
    ) -> None:
        new_name = "new category"
        updated_category = await category_service.update_category(
            category.id, CategoryUpdate(name=new_name, is_visible=False)
        )
        assert updated_category.id == category.id
        assert updated_category.name == new_name
        assert not updated_category.is_visible

    async def test_delete_category(
        self, category_service: CategoryService, category: Category, db_session: AsyncSession
    ) -> None:
        removed_category = await category_service.delete_category(category.id)
        category_in_db = await db_session.execute(
            select(Category).where(Category.id == removed_category.id)
        )
        assert category_in_db.scalars().first() is None

    async def test_delete_nonexisted_category(self, category_service: CategoryService) -> None:
        unexisted_category_id = 123
        with pytest.raises(HTTPException, match="Категория не найдена"):
            await category_service.delete_category(unexisted_category_id)

    async def test_delete_category_with_expenses(
        self, category_service: CategoryService, expense: Expense, db_session: AsyncSession
    ) -> None:
        category_id = expense.category.id

        with pytest.raises(HTTPException, match="Нельзя удалить категорию с тратами"):
            await category_service.delete_category(category_id)

        category_in_db = await db_session.execute(
            select(Category).where(Category.id == category_id)
        )
        assert category_in_db.scalars().first() is not None
