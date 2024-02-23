import httpx
from aiogram import types, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from src.core.engine import dp, bot, TELEGRAM_CHAT_ID, API_URL
from src.telegram.users.user_actions import start_user_data_collection
async def send_to_admin(dp):
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text='Бот запущен')

class SearchForm(StatesGroup):
    query = State()  # Состояние для сохранения запроса

class Form(StatesGroup):
    action = State()
    report_period = State()
    user_action = State()
    create_user = State()
    update_user = State()
    find_user = State()



# Команда start
@dp.message_handler(commands=['start'], state='*')
async def cmd_start(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Клиент", "Отчет")
    await message.answer("Выберите действие:", reply_markup=markup)
    await Form.action.set()


@dp.message_handler(state=Form.action)
async def process_action(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['action'] = message.text
        mes = data['action']
    if mes == "Клиент":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("Создать", "Изменить", "Найти")
        await Form.user_action.set()
        await message.answer("Выберите действие с клиентом:", reply_markup=markup)
    elif mes == "Отчет":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("Выбрать период", "Отметить продленные")
        await Form.report_period.set()
        await message.answer("Выберите действие с отчетом:", reply_markup=markup)
        pass  # логика вызова report.py

@dp.message_handler(state=Form.user_action)
async def process_client_action(message: types.Message, state: FSMContext):
    if message.text == "Создать":
        await start_user_data_collection(message, state)
    elif message.text == "Изменить":
        await message.answer("Введите ID клиента, которого нужно изменить.")
        await message.answer("Введите данные клиента.")
        await start_user_data_collection(message, state)
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
    dp.register_message_handler(cmd_start, commands=['start'], state='*')
    dp.register_message_handler(process_action, state=Form.action)
    dp.register_message_handler(process_client_action, state=Form.user_action)




