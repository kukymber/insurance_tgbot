from aiogram import Dispatcher

from src.core.back_functions import go_back_state
from src.telegram.head import start_callback_handler, process_action, process_client_action
from src.telegram.start import cmd_start
from src.telegram.states.title import Title


def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(go_back_state, lambda message: message == "Назад", state="*")
    dp.register_callback_query_handler(start_callback_handler, lambda c: c.data == 'start')
    dp.register_message_handler(process_action, state=Title.start_action)
    dp.register_message_handler(process_client_action, state=Title.user_action)
