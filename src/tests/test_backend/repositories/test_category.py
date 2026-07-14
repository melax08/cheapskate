import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.category import Category
from backend.app.models.expense import Expense
from backend.app.repositories.category import category_repository
from backend.app.schemas.category import CategoryCreate, CategoryUpdate
from tests.test_backend.factories.category import CategoryFactory
from tests.test_backend.factories.expense import ExpenseFactory


@pytest.mark.anyio
class TestCategoryRepository:
    async def test_create_category(self, db_session: AsyncSession) -> None:
        obj_in = CategoryCreate(name="test", is_visible=True)
        category = await category_repository.create(obj_in, db_session)
        assert category.id is not None
        assert category.name == obj_in.name
        assert category.is_visible

    async def test_delete_category(self, db_session: AsyncSession, category: Category) -> None:
        deleted_category = await category_repository.remove(category, db_session)
        category_in_db = await db_session.execute(
            select(Category).where(Category.id == deleted_category.id)
        )
        assert category_in_db.scalars().first() is None

    async def test_delete_category_with_expenses(
        self, db_session: AsyncSession, expense: Expense
    ) -> None:
        category_id = expense.category.id

        with pytest.raises(IntegrityError):
            async with db_session.begin_nested():
                await category_repository.remove(expense.category, db_session)

        category_in_db = await db_session.execute(
            select(Category).where(Category.id == category_id)
        )
        assert category_in_db.scalars().first() is not None

    async def test_update_category(self, db_session: AsyncSession, category: Category) -> None:
        new_category_name = "new test category"
        obj_in = CategoryUpdate(name=new_category_name, is_visible=False)
        category_db = await category_repository.update(category, obj_in, db_session)
        assert category_db.id == category.id
        assert category_db.name == new_category_name
        assert not category_db.is_visible

    async def test_get_category_by_name(self, db_session: AsyncSession, category: Category) -> None:
        category_db = await category_repository.get_by_name(category.name, db_session)
        assert category_db is category

    async def test_get_all_categories(self, db_session: AsyncSession) -> None:
        visible_categories_count = 7
        hidden_categories_count = 3

        visible_categories = await CategoryFactory.create_batch_async(
            db_session, size=visible_categories_count, is_visible=True
        )
        await CategoryFactory.create_batch_async(
            db_session, size=hidden_categories_count, is_visible=False
        )

        all_categories = await category_repository.get_all_categories(
            session=db_session, only_visible=False
        )
        assert len(all_categories) == visible_categories_count + hidden_categories_count

        only_visible_categories = await category_repository.get_all_categories(
            session=db_session, only_visible=True
        )
        assert only_visible_categories == visible_categories

    async def test_get_all_categories_with_expenses_count(self, db_session: AsyncSession) -> None:
        category_with_expenses = await CategoryFactory.create_async(db_session)
        category_without_expenses = await CategoryFactory.create_async(db_session)
        expected_expenses_count = 3
        await ExpenseFactory.create_batch_async(
            session=db_session, size=expected_expenses_count, category=category_with_expenses
        )

        categories_with_expenses_count = (
            await category_repository.get_all_categories_with_expenses_count(db_session)
        )
        category_expenses_count_mapping = {
            category_data[0]: category_data[1] for category_data in categories_with_expenses_count
        }
        assert category_expenses_count_mapping[category_with_expenses] == expected_expenses_count
        assert category_expenses_count_mapping[category_without_expenses] == 0

    async def test_is_category_has_expenses(self, db_session: AsyncSession) -> None:
        expense_with_category = await ExpenseFactory.create_async(db_session)
        assert (
            await category_repository.is_category_has_expenses(
                expense_with_category.category, db_session
            )
            is True
        )

        category_without_expense = await CategoryFactory.create_async(db_session)
        assert not (
            await category_repository.is_category_has_expenses(category_without_expense, db_session)
        )
