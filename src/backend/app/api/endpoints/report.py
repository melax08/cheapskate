from fastapi import APIRouter, Depends

from backend.app.schemas.report import ReportDB
from backend.app.services.report.report import TableReportService

router = APIRouter()


@router.get("/")
async def get_report(report_service: TableReportService = Depends(TableReportService)) -> ReportDB:
    report = await report_service.get_report_instance()
    return report


@router.post("/update-report")
async def update_report(
    report_service: TableReportService = Depends(TableReportService),
) -> ReportDB:
    report = await report_service.update_google_tables_report()
    return report
