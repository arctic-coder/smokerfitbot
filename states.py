from aiogram.dispatcher.filters.state import State, StatesGroup

class Form(StatesGroup):
    level = State()
    limitations = State()
    equipment = State()
    duration = State()
    email = State()
