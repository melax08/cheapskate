from backend.app.crud.user import user_crud
from backend.app.schemas.user import UserCreate, UserDB
from backend.app.services.base import BaseService


class UserService(BaseService):
    async def get_or_create_or_update_telegram_user(self, user_obj: UserCreate) -> UserDB:
        user = await user_crud.get_by_telegram_id(user_obj.telegram_id, self._session)
        if user:
            return await user_crud.update(user, user_obj, self._session)

        return await user_crud.create(user_obj, self._session)
