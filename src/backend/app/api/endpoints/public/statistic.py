from fastapi import APIRouter, Depends

from backend.app.dependencies.authorization import get_current_user
from backend.app.schemas.statistic import MoneySpent
from backend.app.services.statistic import StatisticService

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/money-spent", response_model=MoneySpent)
async def money_spent(
    statistic_service: StatisticService = Depends(StatisticService),
) -> MoneySpent:
    return await statistic_service.money_spent()
