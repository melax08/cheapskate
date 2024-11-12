from aiogram.fsm.state import State, StatesGroup


class AddCategoryState(StatesGroup):
    writing_category_name = State()
