from pydantic import BaseModel
from datetime import datetime

from .category import CategoryDB


class ExpenseBase(BaseModel):
    amount: float


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
