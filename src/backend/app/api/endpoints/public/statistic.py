from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.db import get_async_session
from backend.app.dependencies.authorization import get_current_user
from backend.app.repositories.setting import setting_repository
from backend.app.schemas.statistic import MoneySpent, MonthYearStatistic, StatisticPeriod
from backend.app.services.statistic import StatisticService

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/money-spent", response_model=MoneySpent)
async def money_spent(
    statistic_service: StatisticService = Depends(StatisticService),
) -> MoneySpent:
    return await statistic_service.money_spent()


@router.get("/periods", response_model=list[StatisticPeriod])
async def years_and_months_with_expenses(
    statistic_service: StatisticService = Depends(StatisticService),
    session: AsyncSession = Depends(get_async_session),
) -> list[StatisticPeriod]:
    default_currency = await setting_repository.get_default_currency(session)
    return await statistic_service.get_statistic_periods(default_currency)


@router.post("", response_model=MonthYearStatistic)
async def statistic_for_period(
    period: StatisticPeriod, statistic_service: StatisticService = Depends(StatisticService)
) -> MonthYearStatistic:
    return await statistic_service.get_month_year_statistic(period)
