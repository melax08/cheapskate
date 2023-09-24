from datetime import datetime

from app.core.constants import MINIMUM_EXPENSE_AMOUNT
from pydantic import BaseModel, Field

from .category import CategoryDB


class ExpenseBase(BaseModel):
    amount: float = Field(..., ge=MINIMUM_EXPENSE_AMOUNT)


class ExpenseCreate(ExpenseBase):
    category_id: int


class ExpenseDB(ExpenseBase):
    id: int
    category: CategoryDB
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
