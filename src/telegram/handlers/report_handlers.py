from aiogram import Dispatcher

from src.telegram.reports.report import start_report, process_action, process_period, process_client_action
from src.telegram.states.report.report_state import ReportData


def register_report_handlers(dp: Dispatcher):
    dp.register_message_handler(start_report, state=ReportData.report_action)
    dp.register_message_handler(process_action, lambda message: message.text.lower() in
                                                                ["выбрать период", "отметить продленные"], state="*")
    dp.register_message_handler(process_period, state=ReportData.input_period)
    dp.register_message_handler(process_client_action, state=ReportData.input_ids_for_extension)
