from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from utils.constants import MINIMUM_EXPENSE_AMOUNT

from .category import CategoryDB
from .currency import CurrencyDB


class ExpenseBase(BaseModel):
    amount: float = Field(..., ge=MINIMUM_EXPENSE_AMOUNT)


class ExpenseCreate(ExpenseBase):
    category_id: int


class ExpenseDB(ExpenseBase):
    id: int
    category: CategoryDB
    currency: Optional[CurrencyDB]

    class Config:
        orm_mode = True


class ExpenseMoneyLeftDB(ExpenseDB):
    money_left: float

    class Config:
        orm_mode = True


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
