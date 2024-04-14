class BadRequest(Exception):
    """Raises if API return 400 status code."""

    pass


class APIError(Exception):
    """Raises if API return 401 and more status code."""

    pass
