from aiogram.fsm.state import State, StatesGroup


class AddCurrency(StatesGroup):
    entering_currency_name = State()
    entering_currency_code = State()
    entering_currency_country = State()
