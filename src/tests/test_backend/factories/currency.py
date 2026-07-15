import factory
from faker import Faker

from backend.app.models.currency import Currency
from configs.constants import (
    COUNTRY_LENGTH,
    MAX_CURRENCY_NAME_LENGTH,
)

from .base import BaseFactory

fake = Faker()


class CurrencyFactory(BaseFactory):
    class Meta:
        model = Currency

    name = factory.LazyFunction(lambda: fake.unique.currency_name()[:MAX_CURRENCY_NAME_LENGTH])
    letter_code = factory.LazyFunction(lambda: fake.unique.currency_code())
    country = factory.LazyFunction(lambda: fake.unique.country()[:COUNTRY_LENGTH])
