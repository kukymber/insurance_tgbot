from datetime import datetime
from typing import Union

import httpx
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.core.back_functions import process_back
from src.core.engine import API_URL, bot
from src.core.server import server_check_decorator, format_date
from src.core.validate import validate_name, validate_phone, validate_email, validate_date, InsuranceInfoEnum
from src.telegram.keyboards.keyboards import create_main_menu, create_client_menu, get_step_keyboard
from src.telegram.states.client.client_state import UserDataState
from src.telegram.states.title import Title


async def edit_client(callback_query: types.CallbackQuery) -> None:
    await UserDataState.user_id.set()
    await callback_query.message.edit_text(
        f"Введите id клиента:", reply_markup=None)


async def process_user_id(message: types.Message, state: FSMContext) -> None:
    await state.update_data(user_id=message.text)
    await start_user_data_collection(message, state)


async def process_text_input(message: types.Message, state: FSMContext, validation_func: callable, current_state,
                             next_state, prompt: str) -> None:
    """
    Обрабатывает текстовый ввод пользователя и переходит к следующему состоянию в случае успешной валидации.
    :param message: Сообщение от пользователя.
    :param state: Контекст состояния пользователя.
    :param validation_func: Функция для валидации введенных данных.
    :param current_state: Текущее состояние в машине состояний.
    :param next_state: Состояние для перехода после успешной валидации.
    :param prompt: Сообщение пользователю после успешной валидации.
    """
    valid, result = validation_func(message.text)
    if not valid:
        await message.answer(result + " Попробуйте еще раз.")
        return
    state_str = current_state.state if hasattr(current_state, 'state') else str(current_state)
    await UserDataState.set_client_previous(state, state_str)

    key_for_data = state_str.split(':')[1]
    await state.update_data({key_for_data: result})

    await next_state.set()
    await message.answer(prompt, reply_markup=await get_step_keyboard())


async def start_user_data_collection(message_or_callback_query: Union[types.Message, types.CallbackQuery],
                                     state: FSMContext) -> None:
    """
    Начинает собирать данные по клиенту.
    Если user_id уже есть в state, значит мы обновляем данные клиента.
    В противном случае - создаем нового клиента.
    """

    data = await state.get_data()
    user_id = data.get('user_id')

    action = 'edit' if user_id else 'create'
    await state.update_data(action=action)

    await UserDataState.first_name.set()
    response_text = f"Введите имя клиента (действие: {('Создать' if action == 'create' else 'Обновить')}):"
    if isinstance(message_or_callback_query, types.CallbackQuery):
        await message_or_callback_query.message.edit_text(response_text, reply_markup=None)
    else:
        await message_or_callback_query.answer(response_text)


async def process_first_name(message: types.Message, state: FSMContext) -> None:
    await process_text_input(message, state, validate_name, UserDataState.first_name, UserDataState.middle_name,
                             "Введите отчество клиента:")


async def process_middle_name(message: types.Message, state: FSMContext) -> None:
    await process_text_input(message, state, validate_name, UserDataState.middle_name, UserDataState.last_name,
                             "Введите фамилию клиента:")


async def process_last_name(message: types.Message, state: FSMContext) -> None:
    await process_text_input(message, state, validate_name, UserDataState.last_name, UserDataState.phone,
                             "Введите телефон клиента:")


async def process_phone(message: types.Message, state: FSMContext) -> None:
    await process_text_input(message, state, validate_phone, UserDataState.phone, UserDataState.email,
                             "Введите почту клиента:")


async def process_email(message: types.Message, state: FSMContext) -> None:
    await process_text_input(message, state, validate_email, UserDataState.email, UserDataState.time_insure_end,
                             "Введите дату окончания полиса в формате дд.мм.гггг:")


async def process_time_insure_end(message: types.Message, state: FSMContext) -> None:
    await UserDataState.set_client_previous(state, UserDataState.time_insure_end.state)

    valid, result = validate_date(message.text)
    if not valid:
        await message.answer(result + " Попробуйте еще раз.")
        return
    await state.update_data(time_insure_end=result)

    markup = InlineKeyboardMarkup()
    for polis_type in InsuranceInfoEnum:
        markup.add(InlineKeyboardButton(text=polis_type.value, callback_data=polis_type.name))

    await message.answer("Выберите тип полиса:", reply_markup=markup)
    await UserDataState.polis_type.set()


async def process_polis_type(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    await UserDataState.set_client_previous(state, UserDataState.polis_type.state)
    polis_type_key = callback_query.data
    polis_type = InsuranceInfoEnum[polis_type_key]

    await state.update_data(polis_type=polis_type_key)
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.edit_text(f"Вы выбрали тип полиса: "
                                           f"{polis_type.value}\nВведите какие-либо важные данные по полису")
    await UserDataState.process_description.set()


async def process_description(message: types.Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await finish_user_data_collection(message, state)


@server_check_decorator
async def finish_user_data_collection(message: types.Message, state: FSMContext) -> None:
    """
    Сбор всей информации в json и отправка на роут POST или PUT запроса.
    """
    data = await state.get_data()
    json_data = {
        "time_create": datetime.now().isoformat(),
        "time_insure_end": data['time_insure_end'],
        "first_name": data['first_name'].title(),
        "middle_name": data['middle_name'].title(),
        "last_name": data['last_name'].title(),
        "phone": data['phone'],
        "email": data['email'],
        "description": data['description'],
        "polis_type": data['polis_type'],
    }
    async with httpx.AsyncClient() as client:
        if data['action'] == 'create':
            url = f"{API_URL}/users/create"
            request = client.post
        elif data['action'] == 'edit':
            url = f"{API_URL}/users/{data.get('user_id')}"
            request = client.put
        else:
            raise ValueError("Не установленно действие! ")
        response = await request(url, json=json_data)

        if response.status_code in (200, 201):
            await message.answer("Данные успешно обработаны.")
            await state.finish()
            await Title.start_action.set()
            markup = await create_main_menu()
            await message.answer("Выберите действие:", reply_markup=markup)
        else:
            await message.answer(f"Произошла ошибка: {response.text}")
            await state.set_data({})
            await Title.user_action.set()
            markup = await create_client_menu()
            await message.answer("Выберите действие:", reply_markup=markup)


async def process_back_wrapper(message: types.Message, state: FSMContext) -> None:
    await process_back(message, state, UserDataState)


async def process_find_user(callback_query: types.CallbackQuery) -> None:
    await UserDataState.input_fio.set()
    await callback_query.message.edit_text(
        f"Введите ФИО клиента для поиска:", reply_markup=None)


@server_check_decorator
async def find_user_fio(message: types.Message, state: FSMContext) -> None:
    fio = message.text
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/users/users/get_all",
                                    params={"search_query": fio, "page": 1, "size": 10})
        if response.status_code == 200:
            data = response.json()
            users = data.get('users', [])
            response_text = f"Данные для поиска '{fio}':\n"
            for user in users:
                user_info = (
                    f"ID клиента: {user['id']}, "
                    f"Фамилия: {user['last_name']}, "
                    f"Имя: {user['first_name']}, "
                    f"Отчество: {user['middle_name']}, "
                    f"Телефон: {user['phone']}, "
                    f"Почта: {user['email']}\n"
                )
                response_text += user_info

                insurances = user.get('insurance', [])
                if insurances:
                    for insurance in insurances:
                        formatted_date = await format_date(insurance['time_insure_end'])
                        insurance_info = (
                            f"ID Полиса: {insurance['id']}, "
                            f"Описание: {insurance['description']}, "
                            f"Дата окончания: {formatted_date}, "
                            f"Тип полиса: {insurance['polis_type']}, "
                            f"Продлен: {'Да' if insurance['polis_extended'] else 'Нет'}\n"
                        )
                        response_text += insurance_info + "\n"
                else:
                    response_text += "  Полисов не найдено\n"
            await message.answer(response_text)
        elif response.status_code == 404:
            await message.answer("Данных по вашему запросу не найдено")
        else:
            await message.answer("Произошла ошибка при получении отчета.")
    await state.finish()
    await Title.start_action.set()
    markup = await create_main_menu()
    await message.answer("Выберите действие:", reply_markup=markup)
