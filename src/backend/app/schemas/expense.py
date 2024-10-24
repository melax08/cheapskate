from datetime import datetime
from decimal import Decimal
from typing import Optional

from configs.constants import MINIMUM_EXPENSE_AMOUNT
from pydantic import BaseModel, ConfigDict, Field

from .category import CategoryDB
from .currency import CurrencyDB


class ExpenseBase(BaseModel):
    amount: Decimal = Field(..., ge=MINIMUM_EXPENSE_AMOUNT)


class ExpenseCreate(ExpenseBase):
    category_id: int
    currency_id: Optional[int] = None


class ExpenseDB(ExpenseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: CategoryDB
    currency: Optional[CurrencyDB]


class ExpenseMoneyLeftDB(ExpenseDB):
    money_left: Decimal


class CategoryExpense(BaseModel):
    name: str
    amount: Decimal


class CurrencyCategoryExpense(BaseModel):
    currency: CurrencyDB
    categories: list[CategoryExpense]
    currency_amount: Decimal


class ExpenseStatistic(BaseModel):
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
                categories_list.append(
                    CategoryExpense(name=category.name, amount=amount)
                )

            currencies.append(
                CurrencyCategoryExpense(
                    currency=currency,
                    categories=categories_list,
                    currency_amount=currency_amount,
                )
            )

        return cls(currencies=currencies, **kwargs)


class ExpenseStatisticSpent(ExpenseStatistic):
    money_spent: Decimal


class MoneyLeft(ExpenseStatisticSpent):
    budget: Decimal
    money_left: Decimal
    current_datetime: datetime
    default_currency: CurrencyDB


class MoneyLeftNew(ExpenseStatisticSpent):
    budget: Decimal
    money_left: Decimal
    current_datetime: datetime
    default_currency: CurrencyDB


class ExpensePeriod(BaseModel):
    year: int
    month: int
