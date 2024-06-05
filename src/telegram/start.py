from typing import Union

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from src.core.state_manger import go_back
from src.core.engine import bot, TELEGRAM_CHAT_ID
from src.telegram.keyboards.keyboards import create_client_menu, create_report_menu, create_main_menu
from src.telegram.states.client.client_state import UserDataState
from src.telegram.states.report.report_state import ReportData
from src.telegram.states.title import Title
from src.telegram.users.client_action import (
    start_user_data_collection
)


async def send_to_admin(dp: Dispatcher) -> None:
    start_button = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Начать работу с ботом", callback_data="start")
    )
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Бот запущен. Нажмите на кнопку ниже, чтобы начать работу.",
                           reply_markup=start_button)

async def start_bot(callback_query: types.CallbackQuery) -> None:
    await callback_query.message.answer("Бот начал работу! Добро пожаловать!")
    await callback_query.answer()


async def process_action(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['action'] = message.text
        mes = data['action']
    if mes == "Клиент":
        await state.update_data(previous_state=Title.start_action)
        markup = create_client_menu()
        await Title.user_action.set()
        await message.answer("Выберите действие с клиентом:", reply_markup=markup)
    elif mes == "Отчет":
        data['previous_state'] = message.text
        markup = create_report_menu()
        await ReportData.report_action.set()
        await message.answer("Выберите действие с отчетом:", reply_markup=markup)


async def process_client_action(message: types.Message, state: FSMContext, callback_query: CallbackQuery) -> None:
    if message.text == "Создать":
        await start_user_data_collection(message, state)
    elif message.text == "Изменить":
        await UserDataState.user_id.set()
        await message.answer("Введите ID клиента, которого нужно изменить.")
    elif message.text == "Найти":
        await Title.find_user.set()
        await message.answer("Введите данные для поиска клиента.")
    elif message.text == "Назад":
        await go_back(callback_query)
