import factory

from backend.app.models.expense import Expense

from .base import BaseFactory
from .category import CategoryFactory
from .currency import CurrencyFactory


class ExpenseFactory(BaseFactory):
    class Meta:
        model = Expense

    category = factory.SubFactory(CategoryFactory)
    currency = factory.SubFactory(CurrencyFactory)
    amount = factory.Faker("random_int", min=1, max=1000)
