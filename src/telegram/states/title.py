from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from src.core.engine import TELEGRAM_CHAT_ID, bot


class Title(StatesGroup):
    start_action = State()
    user_action = State()
    waiting_for_user_id = State()
    create_user = State()
    update_user = State()
    find_user = State()
