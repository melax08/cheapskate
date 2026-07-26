import factory

from backend.app.models.expense import Expense

from .base import BaseFactory
from .category import CategoryFactory
from .currency import CurrencyFactory
from .user import UserFactory


class ExpenseFactory(BaseFactory):
    class Meta:
        model = Expense

    category = factory.SubFactory(CategoryFactory)
    currency = factory.SubFactory(CurrencyFactory)
    amount = factory.Faker("random_int", min=1, max=1000)
    description = factory.Sequence(lambda n: f"Expense {n}")
    user = factory.SubFactory(UserFactory)
