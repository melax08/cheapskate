from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.db import get_async_session
from backend.app.crud.report import report_crud
from backend.app.schemas.report import ReportDB
from backend.app.services.report.report import TableReportService

router = APIRouter()


@router.get("/")
async def get_report(session: AsyncSession = Depends(get_async_session)) -> ReportDB:
    report = await report_crud.get(session)
    return report


@router.post("/update-report")
async def update_report(
    report_service: TableReportService = Depends(TableReportService),
) -> ReportDB:
    report = await report_service.update_google_tables_report()
    return report
