from datetime import datetime

import httpx
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.core.engine import API_URL, bot
from src.telegram.buttons.button import get_step_keyboard, process_back
from src.core.validate import validate_name, validate_phone, validate_email, validate_date, InsuranceInfoEnum
from src.telegram.buttons.button import get_main_menu_keyboard, get_client_action_keyboard
from src.telegram.states.client.client_state import UserDataState
from src.telegram.states.title import Title


async def process_user_id(message: types.Message, state: FSMContext):
    await state.update_data(user_id=message.text)
    await start_user_data_collection(message, state)


async def process_text_input(message: types.Message, state: FSMContext, validation_func, current_state, next_state,
                             prompt):
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
    await message.answer(prompt, reply_markup=get_step_keyboard())


async def start_user_data_collection(message: types.Message, state: FSMContext):
    """
    Начинает собирать данные по клиенту.
    Если user_id уже есть в state, значит мы обновляем данные клиента.
    В противном случае - создаем нового клиента.
    """
    data = await state.get_data()
    user_id = data.get('user_id')

    action = 'обновить' if user_id else 'создать'
    await state.update_data(action=action)

    await UserDataState.first_name.set()
    await message.answer(f"Введите имя клиента (действие: {action}):", reply_markup=None)


async def process_first_name(message: types.Message, state: FSMContext):
    await process_text_input(message, state, validate_name, UserDataState.first_name, UserDataState.middle_name,
                             "Введите отчество клиента:")


async def process_middle_name(message: types.Message, state: FSMContext):
    await process_text_input(message, state, validate_name, UserDataState.middle_name, UserDataState.last_name,
                             "Введите Фамилию клиента:")


async def process_last_name(message: types.Message, state: FSMContext):
    await process_text_input(message, state, validate_name, UserDataState.last_name, UserDataState.phone,
                             "Введите телефон клиента:")


async def process_phone(message: types.Message, state: FSMContext):
    await process_text_input(message, state, validate_phone, UserDataState.phone, UserDataState.email,
                             "Введите почту клиента:")


async def process_email(message: types.Message, state: FSMContext):
    await process_text_input(message, state, validate_email, UserDataState.email, UserDataState.time_insure_end,
                             "Введите время окончания полиса в формате дд.мм.гггг:")


async def process_time_insure_end(message: types.Message, state: FSMContext):
    await UserDataState.set_previous(state, UserDataState.time_insure_end.state)

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


async def process_polis_type(callback_query: types.CallbackQuery, state: FSMContext):
    await UserDataState.set_previous(state, UserDataState.polis_type.state)
    polis_type_key = callback_query.data
    polis_type = InsuranceInfoEnum[polis_type_key]

    await state.update_data(polis_type=polis_type_key)
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.edit_text(
        f"Вы выбрали тип полиса: {polis_type.value}\nВведите какие-либо важные данные по полису"
    )
    await UserDataState.process_description.set()


async def process_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await finish_user_data_collection(message, state)


async def finish_user_data_collection(message: types.Message, state: FSMContext):
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
        if data['action'] == 'создать':
            url = f"{API_URL}/users/create"
            request = client.post
        elif data['action'] == 'обновить':
            url = f"{API_URL}/users/{data.get('user_id')}"
            request = client.put
        else:
            raise ValueError("Не установленно действие! ")
        response = await request(url, json=json_data)

        if response.status_code in (200, 201):
            await message.answer("Данные успешно обработаны.")
            await state.finish()
            await Title.start_action.set()
            markup = get_main_menu_keyboard()
            await message.answer("Выберите действие:", reply_markup=markup)
        else:
            await message.answer(f"Произошла ошибка: {response.text}")
            await state.set_data({})
            await Title.user_action.set()
            markup = get_client_action_keyboard()
            await message.answer("Выберите действие:", reply_markup=markup)


async def process_back_wrapper(message: types.Message, state: FSMContext):
    await process_back(message, state, UserDataState)


async def find_user_fio(message: types.Message, state: FSMContext):
    fio = message.text
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/users/users/get_all/",
                                    params={"search_query": fio, "page": 1, "size": 10})
        if response.status_code == 200:
            data = response.json()
            users = data.get('users', [])
            response_text = f"Данные для поиска '{fio}':\n"
            for user in users:
                user_info = (
                    f"Id: {user['id']}, "
                    f"Фамилия: {user['last_name']}, "
                    f"Имя: {user['first_name']}, "
                    f"Отчество: {user['middle_name']}, "
                    f"Телефон: {user['phone']}, "
                    f"Почта: {user['email']}"
                )
                response_text += user_info + "\n"
            await message.answer(response_text)
        else:
            await message.answer("Произошла ошибка при получении отчета.")
    await state.finish()
    await Title.start_action.set()
    markup = get_main_menu_keyboard()
    await message.answer("Выберите действие:", reply_markup=markup)

