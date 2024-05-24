from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from src.core.engine import TELEGRAM_CHAT_ID, bot


class SearchForm(StatesGroup):
    query = State()


class ReportData(StatesGroup):
    report_action = State()
    input_period = State()
    input_ids_for_extension = State()
