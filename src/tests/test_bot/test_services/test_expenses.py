from decimal import Decimal

import pytest

from bot.services.expenses import parse_and_sum_expenses_from_message


@pytest.mark.parametrize(
    "message, expected_output",
    [
        ("5 1", Decimal("6")),
        ("10 -3 5", Decimal("12")),
        ("12 + 8 - 2", Decimal("18")),
        ("-18 3 + 1 - 5 33", Decimal("14")),
        ("-10 - 1", Decimal("-11")),
        ("20 - 20 + 20 -20 +20-20", Decimal("0")),
        ("50 - -30", Decimal("80")),
        ("50 - +30", Decimal("20")),
        ("50 + -30", Decimal("20")),
        ("23-11+33-2-3", Decimal("40")),
        ("3,3 + 8,2", Decimal("11.5")),
        ("idontknow", Decimal("0")),
        ("-3,3 + 3.8 9.1 -1,1", Decimal("8.5")),
        ("", Decimal("0")),
        ("-9 -3.3 -2,9", Decimal("-15.2")),
    ],
)
def test_parse_and_sum_expenses_from_message(message, expected_output) -> None:
    assert parse_and_sum_expenses_from_message(message) == expected_output
