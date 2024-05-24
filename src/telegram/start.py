from typing import Union

from aiogram import types

from src.telegram.buttons.button import get_main_menu_keyboard
from src.telegram.states.title import Title


async def cmd_start(event: Union[types.Message, types.CallbackQuery]) -> None:
    if isinstance(event, types.Message):
        message = event
    elif isinstance(event, types.CallbackQuery):
        message = event.message
        await event.answer()

    markup = get_main_menu_keyboard()
    await message.answer("Выберите действие:", reply_markup=markup)
    await Title.start_action.set()
