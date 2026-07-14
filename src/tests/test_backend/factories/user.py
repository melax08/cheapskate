import factory

from backend.app.models.user import User

from .base import BaseFactory


class UserFactory(BaseFactory):
    class Meta:
        model = User

    telegram_id = factory.Sequence(lambda n: n)
    telegram_username = factory.Sequence(lambda n: f"username_{n}")
    telegram_first_name = factory.Sequence(lambda n: f"first_name_{n}")
    telegram_last_name = factory.Sequence(lambda n: f"last_name_{n}")
