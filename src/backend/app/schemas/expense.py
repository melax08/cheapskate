from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from configs.constants import MINIMUM_EXPENSE_AMOUNT

from .category import CategoryDB
from .currency import CurrencyDB


class ExpenseBase(BaseModel):
    amount: Decimal = Field(..., ge=MINIMUM_EXPENSE_AMOUNT)


class ExpenseCreate(ExpenseBase):
    category_id: int
    currency_id: int | None = None


class ExpenseDB(ExpenseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: CategoryDB
    currency: CurrencyDB | None


class ExpenseMoneyLeftDB(ExpenseDB):
    money_left: Decimal


class CategoryExpense(BaseModel):
    name: str
    amount: Decimal


class CurrencyCategoryExpense(BaseModel):
    currency: CurrencyDB
    categories: list[CategoryExpense]
    currency_amount: Decimal
