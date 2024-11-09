from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# from telegram import InlineKeyboardButton, InlineKeyboardMarkup
# from bot.constants.constants import BUTTON_ROW_LEN


# async def create_category_keyboard(expense_amount: Decimal) -> InlineKeyboardMarkup:
#     """Create keyboard with categories from API."""
#     async with get_api_client() as client:
#         categories = await client.get_categories()
#
#     if len(categories) == 0:
#         raise ValueError
#
#     keyboard = []
#     row = []
#
#     for category in categories:
#         row.append(
#             InlineKeyboardButton(
#                 category["name"], callback_data=f"{expense_amount:f} {category['id']}"
#             )
#         )
#         if len(row) == BUTTON_ROW_LEN:
#             keyboard.append(row)
#             row = []
#     if len(row) > 0:
#         keyboard.append(row)
#
#     return InlineKeyboardMarkup(keyboard)


# async def create_statistic_years_keyboard(client: APIClient) -> InlineKeyboardMarkup | None:
#     """Create initial statistic keyboard with years and months in callback data."""
#     periods = await client.get_expense_periods()
#
#     if not periods:
#         return None
#
#     year_months_map = defaultdict(list)
#     for period in periods:
#         year_months_map[period["year"]].append(str(period["month"]))
#
#     keyboard = []
#     for year, months in year_months_map.items():
#         keyboard.append(
#             [
#                 InlineKeyboardButton(
#                     str(year), callback_data=f'YEAR {year} {",".join(months)}'
#                 )
#             ]
#         )
#
#     return InlineKeyboardMarkup(keyboard)


# def create_statistic_months_keyboard(year, months) -> InlineKeyboardMarkup:
#     """Create a keyboard with the months of the selected year in which the expenses
#     occurred."""
#     keyboard = []
#     for month in months.split(","):
#         keyboard.append(
#             [
#                 InlineKeyboardButton(
#                     f"{get_russian_month_name(calendar.month_name[int(month)])} {year}",
#                     callback_data=f"REP {year} {month}",
#                 )
#             ]
#         )
#
#     return InlineKeyboardMarkup(keyboard)


# def create_delete_expense_keyboard(
#     expense_id: int, money: Decimal = None
# ) -> InlineKeyboardMarkup:
#     """Creates delete expense button."""
#     return InlineKeyboardMarkup.from_row(
#         [
#             InlineKeyboardButton("Удалить", callback_data=f"DEL {expense_id}"),
#             InlineKeyboardButton("Валюта", callback_data=f"CUR {expense_id} {money}"),
#         ]
#     )


async def create_currency_keyboard(expense_id: int) -> InlineKeyboardMarkup:
    async with get_api_client() as client:
        currencies = await client.get_currencies()

        if len(currencies) == 0:
            raise ValueError

        keyboard = []
        row = []

        for currency in currencies:
            row.append(
                InlineKeyboardButton(
                    currency["name"],
                    callback_data=f'CURC {expense_id} {currency.get("id")}',
                )
            )
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if len(row) > 0:
            keyboard.append(row)

        return InlineKeyboardMarkup(keyboard)


async def select_default_currency_keyboard() -> InlineKeyboardMarkup:
    async with get_api_client() as client:
        currencies = await client.get_currencies()

        if len(currencies) == 0:
            raise ValueError

    keyboard = []
    row = []

    for currency in currencies:
        row.append(
            InlineKeyboardButton(
                currency["name"],
                callback_data=f'DEFAULT_CUR {currency.get("id")}',
            )
        )
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if len(row) > 0:
        keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)


def create_settings_keyboard() -> InlineKeyboardMarkup:
    """Create settings keyboard markup."""
    return InlineKeyboardMarkup.from_row(
        [
            InlineKeyboardButton("Поменять валюту", callback_data="change_currency"),
            InlineKeyboardButton("Поменять бюджет", callback_data="change_budget"),
        ]
    )


settings_markup = create_settings_keyboard()
