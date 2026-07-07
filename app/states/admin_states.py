from aiogram.fsm.state import State, StatesGroup


class AddSlotsStates(StatesGroup):
    waiting_date = State()
    waiting_start_time = State()
    waiting_end_time = State()
    waiting_step = State()


class AddServiceStates(StatesGroup):
    waiting_title = State()
    waiting_description = State()
    waiting_price = State()
    waiting_duration = State()


class UpdatePriceStates(StatesGroup):
    waiting_price = State()


class EditServiceStates(StatesGroup):
    waiting_value = State()


class UpdateTemplateStates(StatesGroup):
    waiting_value = State()


class AddReviewStates(StatesGroup):
    waiting_name = State()
    waiting_text = State()
    waiting_rating = State()