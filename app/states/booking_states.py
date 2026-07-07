from aiogram.fsm.state import State, StatesGroup


class BookingStates(StatesGroup):
    waiting_name = State()
    waiting_contact = State()
