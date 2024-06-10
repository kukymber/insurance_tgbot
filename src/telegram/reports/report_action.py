import httpx
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from src.core.engine import API_URL
from src.core.server import server_check_decorator
from src.telegram.keyboards.keyboards import create_main_menu
from src.telegram.states.report.report_state import ReportData
from src.telegram.states.title import Title

API_URL = "http://127.0.0.1:8000/users/get_all"


async def mark_extend_client(callback_query: types.CallbackQuery) -> None:
    await ReportData.mark_extend.set()
    await callback_query.message.edit_text(
        f"Введите id клиента, либо несколько через запятую :", reply_markup=None)


async def report_period_date(callback_query: types.CallbackQuery) -> None:
    await ReportData.mark_extend.set()
    await callback_query.message.edit_text(
        f"Введите период в формате дд.мм.гггг:", reply_markup=None)


@server_check_decorator
async def process_period(message: types.Message, state: FSMContext):
    period = message.text
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}users/get_all", params={"date_insurance_end": period})
        if response.status_code == 200:
            await message.answer(f"Отчет за период {period}: {response.json()}")
        else:
            await message.answer("Произошла ошибка при получении отчета.")
            await ReportData.report_action.set()
    await state.finish()
    await Title.start_action.set()
    markup = await create_main_menu()
    await message.answer("Выберите действие:", reply_markup=markup)


@server_check_decorator
async def process_client_action(message: types.Message, state: FSMContext):
    user_id = message.text
    data = await state.get_data()
    json_data = {
        "description": "string",
        "polis_type": "string",
        "polis_extended": False,
        "time_insure_end": "2024-04-08",
        "time_create": "2024-04-08T13:11:20.023Z",
        "first_name": "string",
        "middle_name": "string",
        "last_name": "string",
        "phone": "string",
        "email": "user@example.com"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}users/update/{user_id}/", json=json_data)
        if response.status_code == 201:
            await message.answer(f"200")
        else:
            await message.answer("Произошла ошибка при получении отчета.")
            await ReportData.report_action.set()
    await state.finish()


async def process_ids_for_extension(message: types.Message, state: FSMContext):
    ids = message.text
    await state.finish()
