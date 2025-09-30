from contextlib import suppress
from typing import Any

from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds

DEFAULT_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


class GoogleAPIClient:
    STUB_TAB_NAME = "stub_tab"

    def __init__(self, scopes: list[str], credentials: dict[str, str], spreadsheet_id: str) -> None:
        self._credentials = ServiceAccountCreds(scopes=scopes, **credentials)
        self._spreadsheet_id = spreadsheet_id

    async def delete_all_tabs(self, aiogoogle, service):
        spreadsheet = await aiogoogle.as_service_account(
            service.spreadsheets.get(spreadsheetId=self._spreadsheet_id)
        )

        requests = []

        for s in spreadsheet["sheets"]:
            if s["properties"]["title"] != self.STUB_TAB_NAME:
                requests.append({"deleteSheet": {"sheetId": s["properties"]["sheetId"]}})

        if requests:
            await aiogoogle.as_service_account(
                service.spreadsheets.batchUpdate(
                    spreadsheetId=self._spreadsheet_id, json={"requests": requests}
                )
            )

    async def create_stub_tab(self, aiogoogle, service):
        with suppress(Exception):
            await aiogoogle.as_service_account(
                service.spreadsheets.batchUpdate(
                    spreadsheetId=self._spreadsheet_id,
                    json={"requests": {"addSheet": {"properties": {"title": self.STUB_TAB_NAME}}}},
                )
            )

    async def delete_stub_tab(self, aiogoogle, service):
        spreadsheet = await aiogoogle.as_service_account(
            service.spreadsheets.get(spreadsheetId=self._spreadsheet_id)
        )

        target = next(
            (s for s in spreadsheet["sheets"] if s["properties"]["title"] == self.STUB_TAB_NAME),
            None,
        )

        if target:
            sheet_id = target["properties"]["sheetId"]
            request = {"requests": [{"deleteSheet": {"sheetId": sheet_id}}]}

            await aiogoogle.as_service_account(
                service.spreadsheets.batchUpdate(spreadsheetId=self._spreadsheet_id, json=request)
            )

    async def create_tab(self, aiogoogle, service, tab_name: str):
        request = {
            "requests": [
                {
                    "addSheet": {
                        "properties": {
                            "title": tab_name,
                        }
                    }
                }
            ]
        }

        await aiogoogle.as_service_account(
            service.spreadsheets.batchUpdate(spreadsheetId=self._spreadsheet_id, json=request)
        )

    async def update_expenses_in_spreadsheet(self, expenses_data: dict[str, Any]) -> None:
        header = [
            "Категория",
            "Январь",
            "Февраль",
            "Март",
            "Апрель",
            "Май",
            "Июнь",
            "Июль",
            "Август",
            "Сентябрь",
            "Октябрь",
            "Ноябрь",
            "Декабрь",
        ]
        # {"2025": {"Продукты: [0, 1, 0, 25, 33, ...]}}
        async with Aiogoogle(service_account_creds=self._credentials) as aiogoogle:
            service = await aiogoogle.discover("sheets", "v4")

            await self.create_stub_tab(aiogoogle, service)
            await self.delete_all_tabs(aiogoogle, service)

            for year, categories_expenses in expenses_data.items():
                year_table_values = [header]
                for category, month_expenses in categories_expenses.items():
                    year_table_values.append([category, *month_expenses])

                request_body = {"majorDimension": "ROWS", "values": year_table_values}

                await self.create_tab(aiogoogle, service, str(year))
                await aiogoogle.as_service_account(
                    service.spreadsheets.values.update(
                        spreadsheetId=self._spreadsheet_id,
                        range=f"{year}!A1:M150",
                        valueInputOption="USER_ENTERED",
                        json=request_body,
                    )
                )

            with suppress(Exception):
                await self.delete_stub_tab(aiogoogle, service)
