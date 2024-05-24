from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup


def get_step_keyboard() -> ReplyKeyboardMarkup:
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add("Предыдущий шаг")
    return keyboard


async def process_back(message: types.Message, state: FSMContext, class_name: type) -> None:
    await class_name.go_back(state)
    await message.answer("Вы вернулись на предыдущий шаг.")


async def go_back_state(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()

    if 'previous_state' in data:
        previous_state = data['previous_state']
        await previous_state.set()
        await message.answer("Вы вернулись на предыдущий шаг.")
    else:
        await message.answer("Предыдущее состояние не найдено.")
