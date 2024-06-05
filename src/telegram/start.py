from typing import Union

from aiogram import Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.core.engine import bot, TELEGRAM_CHAT_ID
from src.telegram.keyboards.keyboards import create_client_menu, create_main_menu
from src.telegram.states.report.report_state import ReportData
from src.telegram.states.title import Title
from aiogram.dispatcher import FSMContext


async def main_menu(callback_query: types.CallbackQuery) -> None:
    await callback_query.message.edit_text("Главное меню", reply_markup=create_main_menu())
    await Title.start_action.set()


async def client_menu(callback_query: types.CallbackQuery) -> None:
    await callback_query.message.edit_text("Меню клиента", reply_markup=create_client_menu())
    await Title.user_action.set()


async def report_menu(message: types.Message) -> None:
    markup = create_client_menu()
    await message.answer("Меню Клиента", reply_markup=markup)
    await ReportData.report_action.set()


async def send_to_admin(dp: Dispatcher) -> None:
    start_button = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Начать работу с ботом", callback_data="start")
    )
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Бот запущен. Нажмите на кнопку ниже, чтобы начать работу.",
                           reply_markup=start_button)


async def cmd_start(callback_query: types.CallbackQuery) -> None:
    await main_menu(callback_query)

