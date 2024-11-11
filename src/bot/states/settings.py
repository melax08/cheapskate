from aiogram.fsm.state import State, StatesGroup


class ChangeBudgetState(StatesGroup):
    writing_month_budget = State()
