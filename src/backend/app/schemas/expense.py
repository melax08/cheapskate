from datetime import datetime

from pydantic import BaseModel, Field

from .category import CategoryDB
from app.core.constants import MINIMUM_EXPENSE_AMOUNT


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


class MoneyLeft(BaseModel):
    budget: float
    money_spend: float
    money_left: float
    current_datetime: datetime


class CategoryExpense(BaseModel):
    name: str
    amount: float


class TodayExpenses(BaseModel):
    money_spend: float
    categories: list[CategoryExpense]
