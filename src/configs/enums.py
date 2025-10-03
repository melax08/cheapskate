from enum import StrEnum


class APIErrorCode(StrEnum):
    UNKNOWN = "unknown"
    NO_SPREADSHEET_ID = "no_spreadsheet_id"
    CATEGORY_EXISTS = "category_exists"
    CATEGORY_NOT_FOUND = "category_not_found"
    EXPENSE_NOT_FOUND = "expense_not_found"
    BAD_MONTH_YEAR = "bad_month_year"
    CURRENCY_NOT_FOUND = "currency_not_found"
    NOT_UNIQUE_CURRENCY_FIELDS = "not_unique_currency_fields"
