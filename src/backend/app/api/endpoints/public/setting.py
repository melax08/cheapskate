from fastapi import APIRouter, Depends

from backend.app.dependencies.authorization import get_current_user
from backend.app.schemas.setting import SettingDB, SettingUpdate
from backend.app.services.setting import SettingsService

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("", response_model=SettingDB)
async def get_settings(
    settings_service: SettingsService = Depends(SettingsService),
) -> SettingDB:
    return await settings_service.get_settings()


@router.patch("", response_model=SettingDB)
async def settings_partial_update(
    settings_data: SettingUpdate, settings_service: SettingsService = Depends(SettingsService)
) -> SettingDB:
    return await settings_service.update_settings(settings_data)
