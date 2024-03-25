import httpx
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import state
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.core.engine import bot, TELEGRAM_CHAT_ID, API_URL
from src.telegram.buttons.button import get_main_menu_keyboard, get_client_action_keyboard, get_report_action_keyboard
from src.telegram.states.state import Form
from src.telegram.users.user_actions import start_user_data_collection, process_user_id


async def send_to_admin(dp: Dispatcher):
    start_button = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Начать работу с ботом", callback_data="start")
    )
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Бот запущен. Нажмите на кнопку ниже, чтобы начать работу.",
                           reply_markup=start_button)


async def start_callback_handler(callback_query: types.CallbackQuery):
    await cmd_start(callback_query)


async def cmd_start(event):
    if isinstance(event, types.Message):
        message = event
    elif isinstance(event, types.CallbackQuery):
        message = event.message
        await event.answer()

    markup = get_main_menu_keyboard()
    await message.answer("Выберите действие:", reply_markup=markup)
    await Form.action.set()


async def process_action(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['action'] = message.text
        mes = data['action']
    if mes == "Клиент":
        markup = get_client_action_keyboard()
        await Form.user_action.set()
        await message.answer("Выберите действие с клиентом:", reply_markup=markup)
    elif mes == "Отчет":
        markup = get_report_action_keyboard()
        await Form.report_period.set()
        await message.answer("Выберите действие с отчетом:", reply_markup=markup)
        pass  # логика вызова report.py


async def process_client_action(message: types.Message, state: FSMContext):
    if message.text == "Создать":
        await start_user_data_collection(message, state)
    elif message.text == "Изменить":
        await process_user_id(message, state)
    elif message.text == "Найти":
        await message.answer("Введите данные для поиска клиента.")
        period = message.text
        async with httpx.AsyncClient() as client:
            response = await client.get(API_URL, params={"date_insurance_end": period})
            if response.status_code == 200:
                await message.answer(f"Отчет за период {period}: {response.json()}")
            else:
                await message.answer("Произошла ошибка при получении отчета.")
        await state.finish()


def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_callback_query_handler(start_callback_handler, lambda c: c.data == 'start')
    dp.register_message_handler(process_action, state=Form.action)
    dp.register_message_handler(process_client_action, state=Form.user_action)
