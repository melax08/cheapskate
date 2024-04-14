from backend.app.models import Currency

from .base import CRUDBase


class CRUDCurrency(CRUDBase):
    """Class with DB CRUD operations for `Currency` model."""


currency_crud = CRUDCurrency(Currency)
