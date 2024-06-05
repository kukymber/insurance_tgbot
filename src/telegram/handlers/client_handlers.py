from aiogram import Dispatcher

from src.telegram.states.client.client_state import UserDataState
from src.telegram.states.title import Title
from src.telegram.users.client_action import process_back_wrapper, start_user_data_collection, process_first_name, \
    process_middle_name, process_last_name, process_phone, process_email, process_time_insure_end, process_polis_type, \
    process_description, process_user_id, find_user_fio


def register_user_actions_handlers(dp: Dispatcher):
    """
      Регистрация обработчиков
      """
    dp.register_message_handler(process_back_wrapper, lambda message: message.text.lower() == "Пердыдуший шаг",
                                state="*")
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
