from aiogram import Dispatcher

from src.core.state_manger import process_callback, go_back
from src.telegram.start import process_action, process_client_action, start_bot
from src.telegram.states.client.client_state import UserDataState
from src.telegram.states.title import Title
from src.telegram.users.client_action import (
    process_back_wrapper, start_user_data_collection,
    process_first_name, process_middle_name, process_last_name, process_phone,
    process_email, process_time_insure_end, process_polis_type, process_description,
    process_user_id, find_user_fio
)


def register_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(process_back_wrapper,
                                lambda message: message.text.lower() == "предыдущий шаг", state="*")
    dp.register_message_handler(start_user_data_collection,
                                lambda message: message.text.lower() in ["создать", "обновить"], state="*")
    dp.register_message_handler(process_first_name, state=UserDataState.first_name)
    dp.register_message_handler(process_middle_name, state=UserDataState.middle_name)
    dp.register_message_handler(process_last_name, state=UserDataState.last_name)
    dp.register_message_handler(process_phone, state=UserDataState.phone)
    dp.register_message_handler(process_email, state=UserDataState.email)
    dp.register_message_handler(process_time_insure_end, state=UserDataState.time_insure_end)
    dp.register_callback_query_handler(process_polis_type, state=UserDataState.polis_type)
    dp.register_message_handler(process_description, state=UserDataState.process_description)
    dp.register_message_handler(process_user_id, state=UserDataState.user_id)
    dp.register_message_handler(find_user_fio, state=Title.find_user)
    dp.register_callback_query_handler(process_callback)
    dp.register_callback_query_handler(go_back, lambda c: c.data == 'Назад')
    dp.register_callback_query_handler(start_bot, lambda c: c.data == 'start')
    dp.register_message_handler(process_action, state=Title.start_action)
    dp.register_message_handler(process_client_action, state=Title.user_action)
