import datetime as dt
from decimal import Decimal

from sqlalchemy import Integer, and_, desc, distinct, extract, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.crud.setting import setting_crud
from backend.app.models.category import Category
from backend.app.models.currency import Currency
from backend.app.models.expense import Expense

from .base import CRUDBase


class CRUDExpense(CRUDBase):
    """Class with DB CRUD operations for `Expense` model."""

    def _get_period_stmt(self, year: int, month: int, additional_stmts: list[bool] | None = None):
        return and_(
            func.cast(extract("month", self.model.date), Integer) == month,
            func.cast(extract("year", self.model.date), Integer) == year,
            *(additional_stmts or []),
        )

    async def calculate_money_expense_sum(self, where_stmt, session: AsyncSession) -> Decimal:
        """Calculates how much money was spent with specified
        WHERE statement."""
        money_spent = await session.execute(select(func.sum(self.model.amount)).where(where_stmt))
        return money_spent.scalars().first() or Decimal("0")

    async def calculate_money_left(
        self,
        session: AsyncSession,
        budget: int | None = None,
        default_currency: Currency | None = None,
    ) -> Decimal:
        """Calculates how much money is left from the budget for
        the current month in current default currency."""
        current_date = dt.datetime.now()

        if not default_currency:
            default_currency = await setting_crud.get_default_currency(session)

        money_spent = await self.calculate_money_expense_sum(
            self._get_period_stmt(
                year=current_date.year,
                month=current_date.month,
                additional_stmts=[Expense.currency_id == default_currency.id],
            ),
            session,
        )

        if budget is None:
            budget = await setting_crud.get_budget(session)

        return round(budget - money_spent, 3)

    async def calculate_today_expenses(self, session: AsyncSession) -> Decimal:
        """Calculates how much money was spent today."""
        today_expenses = await self.calculate_money_expense_sum(
            self.model.date >= dt.date.today(), session
        )
        return round(today_expenses, 3)

    async def get_years_and_months_with_expenses(self, session: AsyncSession):
        """Gets unique years and months with expenses."""
        periods = await session.execute(
            select(
                distinct(extract("year", self.model.date)).label("year"),
                extract("month", self.model.date).label("month"),
            ).order_by(desc("year"), desc("month"))
        )
        return periods.all()

    async def get_years_with_expenses(self, session: AsyncSession, currency_id: int | None = None):
        filter_by_currency_stmt = [self.model.currency_id == currency_id] if currency_id else []

        years = await session.execute(
            select(distinct(extract("year", self.model.date)).label("year"))
            .where(*filter_by_currency_stmt)
            .order_by(desc("year"))
        )
        return years.scalars().all()

    async def get_expenses_sum_for_year_month(self, year: int, month: int, session: AsyncSession):
        """Get the amount of spent money for specified year and month."""
        money_spent = await self.calculate_money_expense_sum(
            self._get_period_stmt(year, month), session
        )
        return round(money_spent, 2)

    async def set_currency(self, expense: Expense, currency_id: int, session: AsyncSession):
        await session.execute(
            update(self.model).where(self.model.id == expense.id).values(currency_id=currency_id)
        )
        await session.commit()
        await session.refresh(expense)
        return expense

    async def get_expenses_by_year_and_currency(
        self, session: AsyncSession, year: int, currency_id: int
    ):
        result = await session.execute(
            select(
                Category,
                extract("month", self.model.date).label("month"),
                func.sum(self.model.amount).label("total"),
            )
            .join(Currency, self.model.currency_id == Currency.id)
            .join(Category, self.model.category_id == Category.id)
            .where(and_(extract("year", self.model.date) == year, currency_id == currency_id))
            .group_by(Category, "month")
            .order_by("month")
        )
        return result.all()


expense_crud = CRUDExpense(Expense)
