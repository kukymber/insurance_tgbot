from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from src.core.engine import dp, bot, API_URL
import httpx

class ReportForm(StatesGroup):
    choosing_action = State()
    input_period = State()
    input_ids_for_extension = State()

API_URL = "http://127.0.0.1:8000/users/get_all"  # Пример URL к FastAPI

@dp.message_handler(commands=['report'], state='*')
async def start_report(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Выбрать период", "Отметить продленные")
    await message.answer("Выберите действие:", reply_markup=markup)
    await ReportForm.choosing_action.set()

@dp.message_handler(lambda message: message.text not in ["Выбрать период", "Отметить продленные"], state=ReportForm.choosing_action)
async def process_invalid_action(message: types.Message):
    return await message.reply("Пожалуйста, выберите действие из предложенных кнопок.")

@dp.message_handler(state=ReportForm.choosing_action)
async def process_action(message: types.Message, state: FSMContext):
    if message.text == "Выбрать период":
        await ReportForm.input_period.set()
        await message.answer("Введите период в формате дд.мм.гггг")
    elif message.text == "Отметить продленные":
        await ReportForm.input_ids_for_extension.set()
        await message.answer("Укажите ID полисов через запятую, которые были продлены.")

@dp.message_handler(state=ReportForm.input_period)
async def process_period(message: types.Message, state: FSMContext):
    period = message.text
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}users/get_all", params={"date_insurance_end": period})
        if response.status_code == 200:
            await message.answer(f"Отчет за период {period}: {response.json()}")
        else:
            await message.answer("Произошла ошибка при получении отчета.")
    await state.finish()

@dp.message_handler(state=ReportForm.input_ids_for_extension)
async def process_ids_for_extension(message: types.Message, state: FSMContext):
    # Логика отправки ID для пометки продленных полисов
    ids = message.text
    # Пример запроса к другому роуту FastAPI для обновления данных (не реализован в вашем примере)
    await state.finish()


def register_report_handlers(dp: Dispatcher):
    from src.telegram.users.user import Form
    dp.register_message_handler(start_report, state=Form.report_period)
    dp.register_message_handler(process_action, state=Form.action)
    # dp.register_message_handler(process_client_action, state=Form.user_action)
    # dp.register_message_handler(process_action, state=Form.action)
    # dp.register_message_handler(process_client_action, state=Form.user_action)

