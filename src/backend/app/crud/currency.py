from .base import CRUDBase
from backend.app.models import Currency


class CRUDCurrency(CRUDBase):
    """Class with DB CRUD operations for `Currency` model."""


currency_crud = CRUDCurrency(Currency)
