from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from utils.constants import MINIMUM_EXPENSE_AMOUNT

from .category import CategoryDB
from .currency import CurrencyDB


class ExpenseBase(BaseModel):
    amount: float = Field(..., ge=MINIMUM_EXPENSE_AMOUNT)


class ExpenseCreate(ExpenseBase):
    category_id: int
    currency_id: Optional[int] = None


class ExpenseDB(ExpenseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: CategoryDB
    currency: Optional[CurrencyDB]


class ExpenseMoneyLeftDB(ExpenseDB):
    money_left: float


class CategoryExpense(BaseModel):
    name: str
    amount: float


class ExpenseStatistic(BaseModel):
    money_spent: float
    categories: list[CategoryExpense]


class MoneyLeft(ExpenseStatistic):
    budget: float
    money_left: float
    current_datetime: datetime


class ExpensePeriod(BaseModel):
    year: int
    month: int
