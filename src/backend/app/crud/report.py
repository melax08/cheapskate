import datetime as dt

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.report import Report

from .base import SingletonCRUDBase


class CRUDReport(SingletonCRUDBase):
    async def update_update_at(self, session: AsyncSession, report: Report):
        report.updated_at = dt.datetime.now()
        session.add(report)
        await session.commit()
        await session.refresh(report)
        return report


report_crud = CRUDReport(Report)
