from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import User

from .base import RepositoryBase


class UserRepository(RepositoryBase):
    async def get_by_telegram_id(self, telegram_id: int, session: AsyncSession) -> User | None:
        user = await session.execute(
            select(self.model).where(self.model.telegram_id == telegram_id)
        )
        return user.scalars().first()


user_repository = UserRepository(User)
