from aiogram import Dispatcher

from src.core.state_manger import process_callback
from src.telegram.reports.report_action import process_client_action, process_period, mark_extend_client, \
    report_period_date
from src.telegram.start import cmd_start, main_menu, client_menu, report_menu
from src.telegram.states.client.client_state import UserDataState
from src.telegram.states.report.report_state import ReportData
from src.telegram.states.title import Title
from src.telegram.users.client_action import (
    start_user_data_collection,
    process_first_name, process_middle_name, process_last_name, process_phone,
    process_email, process_time_insure_end, process_polis_type, process_description,
    process_user_id, edit_client, find_user_fio, process_find_user
)


def register_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(cmd_start, lambda c: c.data == 'start', state='*')
    dp.register_callback_query_handler(main_menu, lambda c: c.data == 'main_menu', state='*')
    dp.register_callback_query_handler(client_menu, lambda c: c.data == 'client_menu', state=Title.start_action)
    dp.register_callback_query_handler(report_menu, lambda c: c.data == 'report_menu', state=Title.start_action)
    dp.register_callback_query_handler(start_user_data_collection, lambda c: c.data == 'create',
                                       state=Title.user_action)
    dp.register_callback_query_handler(edit_client, lambda c: c.data == 'edit', state=Title.user_action)
    dp.register_callback_query_handler(process_find_user, lambda c: c.data == 'find', state=Title.user_action)
    dp.register_callback_query_handler(report_period_date, lambda c: c.data == 'period_report',
                                       state=ReportData.report_action)
    dp.register_callback_query_handler(mark_extend_client, lambda c: c.data == 'mark_extend',
                                       state=ReportData.report_action)
    dp.register_callback_query_handler(UserDataState.go_back, lambda c: c.data == "предыдущий шаг", state=UserDataState)

    dp.register_message_handler(process_client_action, state=ReportData.mark_extend)
    dp.register_callback_query_handler(process_period, state=ReportData.report_period)

    dp.register_message_handler(find_user_fio, state=UserDataState.input_fio)
    dp.register_message_handler(process_user_id, state=UserDataState.user_id)
    dp.register_message_handler(process_first_name, state=UserDataState.first_name)
    dp.register_message_handler(process_middle_name, state=UserDataState.middle_name)
    dp.register_message_handler(process_last_name, state=UserDataState.last_name)
    dp.register_message_handler(process_phone, state=UserDataState.phone)
    dp.register_message_handler(process_email, state=UserDataState.email)
    dp.register_message_handler(process_time_insure_end, state=UserDataState.time_insure_end)
    dp.register_callback_query_handler(process_polis_type, state=UserDataState.polis_type)
    dp.register_message_handler(process_description, state=UserDataState.process_description)

    dp.register_callback_query_handler(process_callback, lambda c: c.data == 'back', state='*')
