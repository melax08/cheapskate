import asyncio

from backend.app.core.config import settings
from backend.app.crud.expense import expense_crud
from backend.app.crud.report import report_crud
from backend.app.crud.setting import setting_crud
from backend.app.models.currency import Currency
from backend.app.models.report import Report
from backend.app.services.base import BaseService
from backend.app.services.report.google_api import DEFAULT_SCOPES, GoogleAPIClient


class TableReportService(BaseService):
    async def update_google_tables_report(self) -> Report:
        report = await self._get_report_instance()
        expenses_data = await self._collect_expenses_data_for_table()
        client = GoogleAPIClient(
            scopes=DEFAULT_SCOPES,
            credentials=settings.google_service_account_info,
            spreadsheet_id=report.spreadsheet_id,
        )
        await client.update_expenses_in_spreadsheet(expenses_data)
        await report_crud.update_update_at(self._session, report)
        return report

    async def _get_report_instance(self) -> Report:
        # ToDo: update report instance on spreadsheet_id change
        report = await report_crud.get(self._session)
        if not report:
            # ToDo: update to normal exception
            raise ValueError("Some error")

        return report

    async def _collect_expenses_data_for_table(self) -> dict[int, dict[str, list[float]]]:
        application_currency = await setting_crud.get_default_currency(self._session)

        expenses_years = await expense_crud.get_years_with_expenses(
            self._session, currency_id=application_currency.id
        )

        data = {}
        await asyncio.gather(
            *[
                self._update_expenses_by_year(data, year, application_currency)
                for year in expenses_years
            ]
        )
        return data

    async def _update_expenses_by_year(self, data: dict, year: int, currency: Currency) -> None:
        data[year] = {}
        expenses_by_month_and_categories = await expense_crud.get_expenses_by_year_and_currency(
            session=self._session, year=year, currency_id=currency.id
        )
        for category, month, amount in expenses_by_month_and_categories:
            if category.name not in data[year]:
                data[year][category.name] = [0] * 12
            data[year][category.name][int(month) - 1] = float(amount)
