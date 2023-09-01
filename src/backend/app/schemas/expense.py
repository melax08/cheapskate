from pydantic import BaseModel, PositiveInt

from .category import CategoryDB


class ExpenseBase(BaseModel):
    amount: PositiveInt


class ExpenseCreate(ExpenseBase):
    category_id: int


class ExpenseDB(ExpenseBase):
    id: int
    category: CategoryDB
    money_left: int

    class Config:
        orm_mode = True
