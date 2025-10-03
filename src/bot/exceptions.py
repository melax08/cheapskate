from typing import Any

from configs.enums import APIErrorCode


class APIError(Exception):
    """Raised when API returned error."""

    def __init__(
        self, response_data: dict[str, Any], response_info: dict[str, Any] | None = None
    ) -> None:
        super().__init__(response_data)
        if isinstance(response_data["detail"], dict):
            self.error_code = response_data["detail"]["error_code"]
            self.message = response_data["detail"]["message"]
        else:
            self.error_code = APIErrorCode.UNKNOWN
            self.message = response_data["detail"]

        self.info = response_info
