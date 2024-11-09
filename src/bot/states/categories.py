from aiogram.fsm.state import State, StatesGroup


class AddCategory(StatesGroup):
    writing_category_name = State()
