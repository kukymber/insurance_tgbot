from datetime import datetime

import httpx
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from src.core.engine import API_URL
from src.core.validate import validate_name, validate_phone, validate_email, validate_date


class UserDataState(StatesGroup):
    action = State()
    first_name = State()
    middle_name = State()
    last_name = State()
    phone = State()
    email = State()
    time_insure_end = State()


async def start_user_data_collection(message: types.Message, state: FSMContext, action: str):
    await UserDataState.first_name.set()
    async with state.proxy() as data:
        data['action'] = action.lower()
    await process_first_name(message, state)

async def process_first_name(message: types.Message, state: FSMContext):
    await message.answer("Введите имя клиента:")
    valid, result = validate_name(message.text)
    if not valid:
        await message.answer(result + " Попробуйте еще раз.")
        return
    await state.update_data(first_name=result)
    await UserDataState.next()


async def process_last_name(message: types.Message, state: FSMContext):
    await message.answer("Введите отчество клиента:")
    valid, result = validate_name(message.text)
    if not valid:
        await message.answer(result + " Попробуйте еще раз.")
        return
    await state.update_data(last_name=result)
    await UserDataState.next()


async def process_middle_name(message: types.Message, state: FSMContext):
    await message.answer("Введите Фамилию клиента:")
    valid, result = validate_name(message.text)
    if not valid:
        await message.answer(result + " Попробуйте еще раз.")
        return
    await state.update_data(middle_name=result)
    await UserDataState.next()


async def process_phone(message: types.Message, state: FSMContext):
    await message.answer("Введите телефон клиента:")
    valid, result = validate_phone(message.text)
    if not valid:
        await message.answer(result + " Попробуйте еще раз.")
        return
    await state.update_data(phone=result)
    await UserDataState.next()


async def process_email(message: types.Message, state: FSMContext):
    await message.answer("Введите почту клиента:")
    valid, result = validate_email(message.text)
    if not valid:
        await message.answer(result + " Попробуйте еще раз.")
        return
    await state.update_data(email=result)
    await UserDataState.next()


async def process_time_insure_end(message: types.Message, state: FSMContext):
    await message.answer("Введите время окончания полиса в формате дд.мм.гггг:")
    valid, result = validate_date(message.text)
    if not valid:
        await message.answer(result + " Попробуйте еще раз.")
        return
    await state.update_data(time_insure_end=result)
    await finish_user_data_collection(message, state)


async def finish_user_data_collection(message: types.Message, state: FSMContext):
    data = await state.get_data()
    json_data = {
        "time_create": datetime.now().isoformat(),
        "time_insure_end": data['time_insure_end'],
        "middle_name": data['middle_name'],
        "last_name": data['last_name'],
        "phone": data['phone'],
        "email": data['email'],
    }

    async with httpx.AsyncClient() as client:
        url = f"{API_URL}/users/create" if data['action'] == 'создать' else f"{API_URL}/users/update/{data.get('user_id')}"
        response = await client.post(url, json=json_data)

        if response.status_code in (200, 201):
            await message.answer("Данные успешно обработаны.")
        else:
            await message.answer(f"Произошла ошибка: {response.text}")

    await state.finish()


def register_user_actions_handlers(dp: Dispatcher):
    dp.register_message_handler(start_user_data_collection,
                                lambda message: message.text.lower() in ["создать", "обновить"], state="*")
    dp.register_message_handler(process_first_name, state=UserDataState.first_name)
    dp.register_message_handler(process_last_name, state=UserDataState.last_name)
    dp.register_message_handler(process_middle_name, state=UserDataState.middle_name)
    dp.register_message_handler(process_phone, state=UserDataState.phone)
    dp.register_message_handler(process_email, state=UserDataState.email)
    dp.register_message_handler(process_time_insure_end, state=UserDataState.time_insure_end)