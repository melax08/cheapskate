import asyncio
from typing import Any

from fastapi import status

from backend.app.core.config import settings
from backend.app.crud.expense import expense_crud
from backend.app.crud.report import report_crud
from backend.app.crud.setting import setting_crud
from backend.app.models.currency import Currency
from backend.app.models.report import Report
from backend.app.services.base import BaseService
from backend.app.services.report.google_api import DEFAULT_SCOPES, GoogleAPIClient
from backend.app.utils import raise_api_error
from configs.enums import APIErrorCode


class TableReportService(BaseService):
    async def get_report_instance(self) -> Report:
        report = await report_crud.get(self._session)
        if report is None:
            raise_api_error(
                error_code=APIErrorCode.NO_SPREADSHEET_ID,
                message="spreadsheet id не указан в настройках приложения",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return report

    async def update_google_tables_report(self) -> Report:
        report = await self.get_report_instance()
        expenses_data = await self._collect_expenses_data_for_table()
        client = GoogleAPIClient(
            scopes=DEFAULT_SCOPES,
            credentials=settings.google_service_account_info,
            spreadsheet_id=report.spreadsheet_id,
        )
        await client.update_expenses_in_spreadsheet(expenses_data)
        await report_crud.update_update_at(self._session, report)
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

        self._calculate_months_expenses_sum(data)

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

    @staticmethod
    def _calculate_months_expenses_sum(data: dict[int, Any]) -> None:
        for year_expenses_data in data.values():
            total = [0] * 12

            for category_months_expenses in year_expenses_data.values():
                total = [
                    current_total + category_expenses
                    for current_total, category_expenses in zip(
                        total, category_months_expenses, strict=False
                    )
                ]

            year_expenses_data["Итог"] = total
