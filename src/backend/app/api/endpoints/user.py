from fastapi import APIRouter, Depends

from backend.app.schemas.user import UserCreate, UserDB
from backend.app.services.user import UserService

router = APIRouter()


@router.post("/telegram-register", response_model=UserDB)
async def telegram_register(
    user: UserCreate, user_service: UserService = Depends(UserService)
) -> UserDB:
    """Get or update or register telegram user."""
    return await user_service.get_or_create_or_update_telegram_user(user)
