from fastapi import HTTPException, status

from configs.enums import APIErrorCode


def raise_api_error(error_code: APIErrorCode, message: str, status_code: status) -> None:
    """Raise http error with the specified body structure."""
    raise HTTPException(
        status_code=status_code,
        detail={"error_code": error_code, "message": message},
    )
