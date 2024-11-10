from aiogram.filters.callback_data import CallbackData


class ChangeDefaultCurrencyCallback(CallbackData, prefix="ch_def_cur"):
    pass


class ChangeBudgetCallback(CallbackData, prefix="ch_bud"):
    pass


class SelectDefaultCurrencyCallback(CallbackData, prefix="select_def_cur"):
    currency_id: int
