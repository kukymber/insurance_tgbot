from aiogram import Dispatcher

from src.core.state_manger import process_callback, go_back
from src.telegram.keyboards.keyboards import create_client_menu
from src.telegram.start import cmd_start, main_menu, client_menu, report_menu
from src.telegram.states.client.client_state import UserDataState
from src.telegram.states.title import Title
from src.telegram.users.client_action import (
    process_back_wrapper, start_user_data_collection,
    process_first_name, process_middle_name, process_last_name, process_phone,
    process_email, process_time_insure_end, process_polis_type, process_description,
    process_user_id, find_user_fio
)


def register_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(cmd_start, lambda c: c.data == 'start')
    dp.register_callback_query_handler(client_menu, lambda c: c.data == 'client_menu', state=Title.start_action)
    dp.register_callback_query_handler(report_menu, lambda c: c.data == 'report_menu', state=Title.start_action)
    dp.register_message_handler(process_back_wrapper,
                                lambda message: message.text.lower() == "предыдущий шаг", state=UserDataState)
    dp.register_callback_query_handler(start_user_data_collection,
                                       lambda c: c.data in ["создать", "обновить"], state=Title.user_action)
    dp.register_message_handler(process_first_name, state=UserDataState.first_name)
    dp.register_message_handler(process_middle_name, state=UserDataState.middle_name)
    dp.register_message_handler(process_last_name, state=UserDataState.last_name)
    dp.register_message_handler(process_phone, state=UserDataState.phone)
    dp.register_message_handler(process_email, state=UserDataState.email)
    dp.register_message_handler(process_time_insure_end, state=UserDataState.time_insure_end)
    dp.register_callback_query_handler(process_polis_type, state=UserDataState.polis_type)
