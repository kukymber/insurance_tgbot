import httpx
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from src.core.engine import API_URL
from src.telegram.states.report.report_state import ReportData

API_URL = "http://127.0.0.1:8000/users/get_all"


async def start_report(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Выбрать период", "Отметить продленные")
    await message.answer("Выберите действие:", reply_markup=markup)


# @dp.message_handler(lambda message: message.text not in ["Выбрать период", "Отметить продленные"],
#                     state=ReportData.report_period)
# async def process_invalid_action(message: types.Message):
#     return await message.reply("Пожалуйста, выберите действие из предложенных кнопок.")

async def process_action(message: types.Message, state: FSMContext):
    if message.text == "Выбрать период":
        await ReportData.input_period.set()
        await message.answer("Введите период в формате дд.мм.гггг")
    elif message.text == "Отметить продленные":
        await ReportData.input_ids_for_extension.set()
        await message.answer("Укажите ID полисов через запятую, которые были продлены.")


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



