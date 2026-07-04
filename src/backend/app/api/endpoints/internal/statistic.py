from fastapi import APIRouter, Depends

from backend.app.schemas.statistic import MoneyLeft, Statistic, StatisticPeriod
from backend.app.services.statistic import StatisticService
from configs.api_settings import (
    MONEY_LEFT_PATH,
    PERIOD_EXPENSE_PATH,
    STATISTIC_PATH,
    TODAY_EXPENSE_PATH,
)

router = APIRouter()


@router.get(MONEY_LEFT_PATH, response_model=MoneyLeft)
async def get_money_left(
    statistic_service: StatisticService = Depends(StatisticService),
) -> MoneyLeft:
    """Get information about the current mount budget, money left and money spent."""
    return await statistic_service.get_money_left()


@router.get(TODAY_EXPENSE_PATH, response_model=Statistic)
async def get_today_expenses(
    statistic_service: StatisticService = Depends(StatisticService),
) -> Statistic:
    """Get the information about today expenses."""
    return await statistic_service.get_today_expenses()


@router.get(PERIOD_EXPENSE_PATH, response_model=list[StatisticPeriod])
async def get_years_and_months_with_expenses(
    statistic_service: StatisticService = Depends(StatisticService),
) -> list[StatisticPeriod]:
    """Get the list of years and months with expenses."""
    return await statistic_service.get_statistic_periods()


@router.post(STATISTIC_PATH, response_model=Statistic)
async def get_statistic_for_period(
    period: StatisticPeriod, statistic_service: StatisticService = Depends(StatisticService)
) -> Statistic:
    """Get the information about expenses for specified month and year."""
    return await statistic_service.get_statistic_for_period(period)
