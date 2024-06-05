from typing import Union

from aiogram import types

from src.telegram.keyboards.keyboards import create_main_menu
from src.telegram.states.title import Title


async def cmd_start(event: Union[types.Message, types.CallbackQuery]) -> None:
    if isinstance(event, types.Message):
        message = event
    elif isinstance(event, types.CallbackQuery):
        message = event.message
        await event.answer()

    markup = create_main_menu()
    await message.answer("Выберите действие:", reply_markup=markup)
    await Title.start_action.set()
