from backend.app.repositories import user_repository
from backend.app.schemas.user import UserCreate, UserDB
from backend.app.services.base import BaseService


class UserService(BaseService):
    async def get_or_create_or_update_telegram_user(self, user_obj: UserCreate) -> UserDB:
        user = await user_repository.get_by_telegram_id(user_obj.telegram_id, self._session)
        if user:
            return await user_repository.update(user, user_obj, self._session)

        return await user_repository.create(user_obj, self._session)
