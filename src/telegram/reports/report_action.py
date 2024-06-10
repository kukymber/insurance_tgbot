import httpx
from aiogram import types
from aiogram.dispatcher import FSMContext

from src.core.engine import API_URL
from src.core.server import server_check_decorator, format_date, insurance_type_map
from src.telegram.keyboards.keyboards import create_main_menu
from src.telegram.states.report.report_state import ReportData
from src.telegram.states.title import Title


async def mark_extend_client(callback_query: types.CallbackQuery) -> None:
    await ReportData.mark_extend.set()
    await callback_query.message.edit_text(
        f"Введите id клиента, либо несколько через запятую :", reply_markup=None)


async def report_period_date(callback_query: types.CallbackQuery) -> None:
    await ReportData.report_period.set()
    await callback_query.message.edit_text(
        f"Введите период в формате дд.мм.гггг:", reply_markup=None)


@server_check_decorator
async def process_period(message: types.Message, state: FSMContext):
    period = message.text
    async with httpx.AsyncClient() as client:
        formatted_period = await format_date(period)
        response = await client.get(f"{API_URL}/users/users/get_all",
                                    params={"date_insurance_end": formatted_period, "page": 1, "size": 10})
        if response.status_code == 200:
            data = response.json()
            users = data.get('users', [])
            response_text = f"Отчет за период '{period}':\n"
            for user in users:
                insurances = user.get('insurance', [])
                insurance_texts = []
                if insurances:
                    for insurance in insurances:
                        if not insurance['polis_extended']:
                            formatted_date = await format_date(insurance['time_insure_end'])
                            insurance_type = insurance_type_map.get(insurance['polis_type'], insurance['polis_type'])
                            insurance_info = (
                                f"Описание: {insurance['description']}, "
                                f"Дата окончания: {formatted_date}, "
                                f"Тип полиса: {insurance_type}, "
                                f"Продлен: {'Да' if insurance['polis_extended'] else 'Нет'}\n"
                            )
                            insurance_texts.append(insurance_info)
                if insurance_texts:
                    user_info = (
                        f"Фамилия: {user['last_name']}, "
                        f"Имя: {user['first_name']}, "
                        f"Отчество: {user['middle_name']}, "
                        f"Телефон: {user['phone']}\n"
                    )
                    response_text += user_info + "".join(insurance_texts) + "\n"
            if response_text == f"Отчет за период '{period}':\n":
                response_text += "Полисов для продления не найдено\n"
            await message.answer(response_text)
        else:
            await message.answer("Произошла ошибка при получении отчета.")
    await state.finish()
    await Title.start_action.set()
    markup = await create_main_menu()
    await message.answer("Выберите действие:", reply_markup=markup)


@server_check_decorator
async def process_client_extend(message: types.Message, state: FSMContext):
    clients_id = message.text.split(',')
    clients_id = [int(client_id.strip()) for client_id in clients_id]

    async with httpx.AsyncClient() as client:
        response = await client.put(f"{API_URL}/users/users/update_insurance", params={"user_ids": clients_id})
        if response.status_code == 200:
            await message.answer("Страховки успешно обновлены.")
        else:
            await message.answer("Произошла ошибка при обновлении страховок.")

    await state.finish()
    await Title.start_action.set()
    markup = await create_main_menu()
    await message.answer("Выберите действие:", reply_markup=markup)


