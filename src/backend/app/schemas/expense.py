from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from configs.constants import MAX_EXPENSE_DESCRIPTION_LENGTH, MINIMUM_EXPENSE_AMOUNT

from .category import CategoryDB
from .currency import CurrencyDB


class ExpenseBase(BaseModel):
    amount: Decimal = Field(..., ge=MINIMUM_EXPENSE_AMOUNT)
    description: str | None = Field(None, max_length=MAX_EXPENSE_DESCRIPTION_LENGTH)


class ExpenseCreate(ExpenseBase):
    category_id: int
    currency_id: int | None = None


class ExpenseCreateWithUser(ExpenseCreate):
    user_telegram_id: int | None = Field(None)


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


class ExpenseUpdate(BaseModel):
    amount: Decimal | None = Field(None, ge=MINIMUM_EXPENSE_AMOUNT)
    description: str | None = Field(None, max_length=MAX_EXPENSE_DESCRIPTION_LENGTH)
    category_id: int | None = Field(None)
    currency_id: int | None = Field(None)
