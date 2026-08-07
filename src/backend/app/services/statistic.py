import calendar
import datetime as dt
from collections import defaultdict
from decimal import Decimal
from operator import itemgetter

from backend.app.api.validators import validate_month_year
from backend.app.models.currency import Currency
from backend.app.repositories import currency_repository, expense_repository, setting_repository
from backend.app.schemas.statistic import (
    CategoryExpense,
    ExpensesStatisticByCategories,
    MoneyLeft,
    MoneySpent,
    MonthYearStatistic,
    Statistic,
    StatisticPeriod,
)
from backend.app.services.base import BaseService


class StatisticService(BaseService):
    """Service to get the expense statistics."""

    async def get_money_left(self) -> MoneyLeft:
        """Get the information about the current month money left."""
        settings = await setting_repository.get(self._session)
        money_left = await expense_repository.calculate_money_left(
            session=self._session,
            budget=settings.budget,
            default_currency=settings.default_currency,
        )
        expenses = await currency_repository.get_this_month_expenses_by_currencies_and_categories(
            self._session
        )

        return MoneyLeft.from_db_query(
            crud_result=expenses,
            budget=settings.budget,
            money_left=money_left,
            money_spent=round(settings.budget - money_left, 2),
            current_datetime=dt.datetime.now(),
            default_currency=settings.default_currency,
        )

    async def get_today_expenses(self) -> Statistic:
        """Get the information about today expenses by currencies and categories."""
        expenses = await currency_repository.get_today_expenses_by_currencies_and_categories(
            self._session
        )
        return Statistic.from_db_query(crud_result=expenses)

    async def get_statistic_periods(
        self, currency: Currency | None = None
    ) -> list[StatisticPeriod]:
        """Get periods with expenses."""
        periods = await expense_repository.get_years_and_months_with_expenses(
            self._session, currency
        )
        return [StatisticPeriod(year=year, month=month) for year, month in periods]

    async def get_statistic_for_period(self, period: StatisticPeriod) -> Statistic:
        """Get the information about expenses by currencies and categories
        for the specified period."""
        validate_month_year(period.year, period.month)
        expenses = await currency_repository.get_expenses_by_currencies_and_categories_for_period(
            period.year, period.month, self._session
        )
        return Statistic.from_db_query(crud_result=expenses)

    async def money_spent(self) -> MoneySpent:
        settings = await setting_repository.get(self._session)
        money_spent = await expense_repository.calculate_money_spent_this_month(
            session=self._session, default_currency=settings.default_currency
        )

        return MoneySpent(
            budget=settings.budget,
            money_spent=money_spent,
            current_datetime=dt.datetime.now(),
            default_currency=settings.default_currency,
        )

    async def get_month_year_statistic(self, period: StatisticPeriod) -> MonthYearStatistic:
        default_currency = await setting_repository.get_default_currency(self._session)
        expenses_by_categories_and_days = (
            await expense_repository.get_categories_expenses_by_days_in_month(
                self._session, period.year, period.month, default_currency
            )
        )

        days_categories_expenses_mapping = defaultdict(dict)
        for category, amount, day in expenses_by_categories_and_days:
            days_categories_expenses_mapping[day][category.name] = amount

        days_result = []
        summary_total = Decimal(0)
        summary_categories = defaultdict(Decimal)

        month_year_days = self._get_month_year_days(period.year, period.month)

        for day in month_year_days:
            day_data = {
                "date": dt.datetime(day=day, month=period.month, year=period.year).strftime(
                    "%Y-%m-%d"
                ),
                "total": Decimal(0),
                "categories": [],
            }
            if day in days_categories_expenses_mapping:
                for category_name, amount in days_categories_expenses_mapping[day].items():
                    day_data["categories"].append(
                        {
                            "name": category_name,
                            "amount": amount,
                        }
                    )
                    day_data["total"] += amount
                    summary_total += amount
                    summary_categories[category_name] += amount

            days_result.append(day_data)

        sorted_summary_categories = dict(
            sorted(summary_categories.items(), key=itemgetter(1), reverse=True)
        )

        now = dt.datetime.now()
        current_year = now.year
        current_month = now.month
        days_passed_in_month = Decimal(
            now.day
            if current_year == period.year and current_month == period.month
            else len(month_year_days)
        )
        average_per_day = summary_total / days_passed_in_month

        return MonthYearStatistic(
            period=period,
            currency=default_currency,
            days=days_result,
            summary=ExpensesStatisticByCategories(
                **{
                    "total": summary_total,
                    "categories": [
                        CategoryExpense(name=category_name, amount=total)
                        for category_name, total in sorted_summary_categories.items()
                    ],
                }
            ),
            average_per_day=average_per_day,
        )

    def _get_month_year_days(self, year: int, month: int) -> list[int]:
        _, num_days = calendar.monthrange(year, month)
        return list(range(1, num_days + 1))
