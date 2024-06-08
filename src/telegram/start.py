from typing import Union
from aiogram import Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.core.engine import bot, TELEGRAM_CHAT_ID
from src.core.state_manger import switch_state
from src.telegram.states.report.report_state import ReportData
from src.telegram.states.title import Title

async def main_menu(callback_query: types.CallbackQuery) -> None:
    user_id = callback_query.from_user.id
    await switch_state(user_id, 'main_menu', callback_query.message)
    await Title.start_action.set()

async def client_menu(callback_query: types.CallbackQuery) -> None:
    user_id = callback_query.from_user.id
    await switch_state(user_id, 'client_menu', callback_query.message)
    await Title.user_action.set()

async def report_menu(callback_query: types.CallbackQuery) -> None:
    user_id = callback_query.from_user.id
    await switch_state(user_id, 'report_menu', callback_query.message)
    await ReportData.report_action.set()

async def send_to_admin(dp: Dispatcher) -> None:
    start_button = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Начать работу с ботом", callback_data="start")
    )
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Бот запущен. Нажмите на кнопку ниже, чтобы начать работу.",
                           reply_markup=start_button)

async def cmd_start(callback_query: types.CallbackQuery) -> None:
    await main_menu(callback_query)
