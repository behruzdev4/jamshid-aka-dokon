from aiogram.fsm.state import State, StatesGroup


class OrderStates(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    waiting_address = State()


class PCBuilderStates(StatesGroup):
    choosing_purpose = State()


class AdminCategoryStates(StatesGroup):
    waiting_name = State()


class AdminProductStates(StatesGroup):
    choosing_category = State()
    waiting_name = State()
    waiting_price = State()
    waiting_description = State()
    waiting_photo = State()


class AdminBroadcastStates(StatesGroup):
    waiting_message = State()


class AdminChannelStates(StatesGroup):
    waiting_link = State()
