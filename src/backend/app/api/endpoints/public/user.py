from fastapi import APIRouter, Depends

from backend.app.dependencies.authorization import get_current_user
from backend.app.schemas.user import UserDB
from backend.app.services.user import UserService

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[UserDB])
async def users_list(
    user_service: UserService = Depends(UserService),
) -> list[UserDB]:
    return await user_service.get_users_list()
