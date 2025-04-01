from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from .currency import CurrencyDB
from .expense import CategoryExpense, CurrencyCategoryExpense


class Statistic(BaseModel):
    currencies: list[CurrencyCategoryExpense]

    @classmethod
    def from_db_query(cls, crud_result: list, **kwargs):
        """
        Create expense statistic schema from database query result of the currency
        crud method: _select_currencies_categories_expenses
        """
        expense_statistic_result = {}
        for currency, category, expense_amount in crud_result:
            if currency not in expense_statistic_result:
                expense_statistic_result[currency] = {}
            expense_statistic_result[currency][category] = expense_amount

        currencies = []
        for currency, categories in expense_statistic_result.items():
            categories_list = []
            currency_amount = 0
            for category, amount in categories.items():
                currency_amount += amount
                categories_list.append(CategoryExpense(name=category.name, amount=amount))

            currencies.append(
                CurrencyCategoryExpense(
                    currency=currency,
                    categories=categories_list,
                    currency_amount=currency_amount,
                )
            )

        return cls(currencies=currencies, **kwargs)


class StatisticSpent(Statistic):
    money_spent: Decimal


class MoneyLeft(StatisticSpent):
    budget: Decimal
    money_left: Decimal
    current_datetime: datetime
    default_currency: CurrencyDB


class StatisticPeriod(BaseModel):
    year: int
    month: int
