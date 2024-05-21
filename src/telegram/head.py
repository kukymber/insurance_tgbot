from aiogram import types, Dispatcher
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.core.engine import bot, TELEGRAM_CHAT_ID
from src.core.general_button import go_back_state
from src.telegram.buttons.button import get_client_action_keyboard, get_report_action_keyboard
from src.telegram.start import cmd_start
from src.telegram.states.state import Form, UserDataState, ReportData
from src.telegram.users.user_actions import start_user_data_collection


async def send_to_admin(dp: Dispatcher):
    start_button = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Начать работу с ботом", callback_data="start")
    )
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Бот запущен. Нажмите на кнопку ниже, чтобы начать работу.",
                           reply_markup=start_button)


async def start_callback_handler(callback_query: types.CallbackQuery):
    await cmd_start(callback_query)


async def process_action(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['action'] = message.text
        mes = data['action']
    if mes == "Клиент":
        await state.update_data(previous_state=Form.action)
        markup = get_client_action_keyboard()
        await Form.user_action.set()
        await message.answer("Выберите действие с клиентом:", reply_markup=markup)
    elif mes == "Отчет":
        data['previous_state'] = message.text
        markup = get_report_action_keyboard()
        await ReportData.report_action.set()
        await message.answer("Выберите действие с отчетом:", reply_markup=markup)


async def process_client_action(message: types.Message, state: FSMContext):
    if message.text == "Создать":
        await start_user_data_collection(message, state)
    elif message.text == "Изменить":
        await UserDataState.user_id.set()
        await message.answer("Введите ID клиента, которого нужно изменить.")
    elif message.text == "Найти":
        await Form.find_user.set()
        await message.answer("Введите данные для поиска клиента.")
    elif message.text == "Назад":
        await go_back_state(message, state)


def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(go_back_state, lambda message: message == "Назад", state="*")
    dp.register_callback_query_handler(start_callback_handler, lambda c: c.data == 'start')
    dp.register_message_handler(process_action, state=Form.action)
    dp.register_message_handler(process_client_action, state=Form.user_action)
