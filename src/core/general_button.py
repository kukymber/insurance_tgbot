from aiogram import types
from aiogram.dispatcher import FSMContext


def get_step_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add("Назад")
    return keyboard


async def process_back(message: types.Message, state: FSMContext, class_name):
    await class_name.go_back(state)
    await message.answer("Вы вернулись на предыдущий шаг.")
