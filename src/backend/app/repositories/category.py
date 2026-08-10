from sqlalchemy import Date, Integer, and_, desc, exists, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import Category, Currency, Expense

from .base import RepositoryBase


class CategoryRepository(RepositoryBase):
    """Repository with DB operations for `Category` model."""

    async def get_by_name(self, category_name: str, session: AsyncSession) -> Category | None:
        db_obj = await session.execute(select(self.model).where(self.model.name == category_name))
        return db_obj.scalars().first()

    async def get_all_categories(self, only_visible: bool, session: AsyncSession):
        if only_visible:
            db_objs = await session.execute(select(self.model).where(self.model.is_visible == True))  # noqa
        else:
            db_objs = await session.execute(select(self.model))

        return db_objs.scalars().all()

    async def get_all_categories_with_expenses_count(self, session: AsyncSession):
        db_objs = await session.execute(
            select(self.model, func.count(Expense.id).label("expenses_count"))
            .outerjoin(Expense, Expense.category_id == Category.id)
            .group_by(Category.id)
            .order_by(Category.id)
        )
        return db_objs

    async def is_category_has_expenses(self, category: Category, session: AsyncSession) -> bool:
        return await session.scalar(select(exists().where(Expense.category_id == category.id)))

    async def get_categories_expenses_by_days_in_month(
        self, session: AsyncSession, year: int, month: int, currency: Currency
    ):
        result = await session.execute(
            select(
                Category,
                func.sum(Expense.amount).label("category_expense_amount"),
                func.cast(extract("day", Expense.date), Integer).label("expenses_day"),
            )
            .join(Expense, Expense.category_id == Category.id)
            .join(Currency, Expense.currency_id == Currency.id)
            .where(
                and_(
                    func.cast(extract("month", Expense.date), Integer) == month,
                    func.cast(extract("year", Expense.date), Integer) == year,
                    Expense.currency_id == currency.id,
                )
            )
            .group_by(Category, "expenses_day")
            .order_by(desc("category_expense_amount"))
        )
        return result.all()

    async def get_today_categories_expenses(self, session: AsyncSession, currency: Currency):
        result = await session.execute(
            select(
                Category.name,
                func.sum(Expense.amount).label("category_expense_amount"),
            )
            .join(Expense, Expense.category_id == Category.id)
            .join(Currency, Expense.currency_id == Currency.id)
            .where(
                and_(
                    Expense.currency_id == currency.id,
                    func.cast(Expense.date, Date) == func.current_date(),
                )
            )
            .group_by(Category.name)
            .order_by(desc("category_expense_amount"))
        )

        return result.all()


category_repository = CategoryRepository(Category)
