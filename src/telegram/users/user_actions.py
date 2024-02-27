from datetime import datetime

import httpx
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.core.engine import API_URL, bot, TELEGRAM_CHAT_ID
from src.core.validate import validate_name, validate_phone, validate_email, validate_date, InsuranceInfoEnum


class UserDataState(StatesGroup):
    action = State()
    first_name = State()
    middle_name = State()
    last_name = State()
    phone = State()
    email = State()
    time_insure_end = State()
    polis_type = State()
    process_description = State()


async def start_user_data_collection(message: types.Message, state: FSMContext):
    await UserDataState.action.set()
    async with state.proxy() as data:
        data['action'] = message.text.lower()
    await message.answer("Введите имя клиента:", reply_markup=None)
    await UserDataState.first_name.set()


async def process_first_name(message: types.Message, state: FSMContext):
    valid, result = validate_name(message.text)
    if not valid:
        await message.answer(result + " Попробуйте еще раз.")
        return
    await state.update_data(first_name=result)
    await message.answer("Введите отчество клиента:")
    await UserDataState.next()


async def process_middle_name(message: types.Message, state: FSMContext):
    valid, result = validate_name(message.text)
    if not valid:
        await message.answer(result + " Попробуйте еще раз.")
        return
    await state.update_data(middle_name=result)
    await message.answer("Введите Фамилию клиента:")

    await UserDataState.next()


async def process_last_name(message: types.Message, state: FSMContext):
    valid, result = validate_name(message.text)
    if not valid:
        await message.answer(result + " Попробуйте еще раз.")
        return
    await state.update_data(last_name=result)
    await message.answer("Введите телефон клиента:")
    await UserDataState.next()


async def process_phone(message: types.Message, state: FSMContext):
    valid, result = validate_phone(message.text)
    if not valid:
        await message.answer(result + " Попробуйте еще раз.")
        return
    await state.update_data(phone=result)
    await message.answer("Введите почту клиента:")
    await UserDataState.next()


async def process_email(message: types.Message, state: FSMContext):
    valid, result = validate_email(message.text)
    if not valid:
        await message.answer(result + " Попробуйте еще раз.")
        return
    await state.update_data(email=result)
    await message.answer("Введите время окончания полиса в формате дд.мм.гггг:")
    await UserDataState.next()


async def process_time_insure_end(message: types.Message, state: FSMContext):
    valid, result = validate_date(message.text)
    if not valid:
        await message.answer(result + " Попробуйте еще раз.")
        return
    await state.update_data(time_insure_end=result)

    markup = InlineKeyboardMarkup()
    for polis_type in InsuranceInfoEnum:
        markup.add(InlineKeyboardButton(text=polis_type.value, callback_data=polis_type.name))

    await message.answer("Выберите тип полиса:", reply_markup=markup)

    await UserDataState.next()


async def process_polis_type(callback_query: types.CallbackQuery, state: FSMContext):
    polis_type = callback_query.data
    await state.update_data(polis_type=polis_type)
    await bot.answer_callback_query(callback_query.id, text=callback_query.data)
    await callback_query.message.edit_text(f"Вы выбрали тип полиса: {polis_type}\nВведите какие-либо важные данные по полису", reply_markup=None)
    await UserDataState.process_description.set()


async def process_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await finish_user_data_collection(message, state)


async def finish_user_data_collection(message: types.Message, state: FSMContext):
    data = await state.get_data()
    json_data = {
        "time_create": datetime.now().isoformat(),
        "time_insure_end": data['time_insure_end'],
        "first_name": data['first_name'],
        "middle_name": data['middle_name'],
        "last_name": data['last_name'],
        "phone": data['phone'],
        "email": data['email'],
        "description": data['description'],
        "polis_type": data['polis_type'],
    }

    async with (httpx.AsyncClient() as client):
        if data['action'] == 'создать':
            url = f"{API_URL}/users/create"
            request = client.post
        else:
            f"{API_URL}/users/{data.get('user_id')}"
            request = client.put
        response = await request(url, json=json_data)

        if response.status_code in (200, 201):
            await message.answer("Данные успешно обработаны.")
        else:
            await message.answer(f"Произошла ошибка: {response.text}")

    await state.finish()


def register_user_actions_handlers(dp: Dispatcher):
    dp.register_message_handler(start_user_data_collection,
                                lambda message: message.text.lower() in ["создать", "обновить"], state="*")
    dp.register_message_handler(process_first_name, state=UserDataState.first_name)
    dp.register_message_handler(process_middle_name, state=UserDataState.middle_name)
    dp.register_message_handler(process_last_name, state=UserDataState.last_name)
    dp.register_message_handler(process_phone, state=UserDataState.phone)
    dp.register_message_handler(process_email, state=UserDataState.email)
    dp.register_message_handler(process_time_insure_end, state=UserDataState.time_insure_end)
    dp.register_callback_query_handler(process_polis_type, state=UserDataState.polis_type)
    dp.register_message_handler(process_description, state=UserDataState.process_description)

