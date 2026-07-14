import factory

from backend.app.models.category import Category

from .base import BaseFactory


class CategoryFactory(BaseFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")
