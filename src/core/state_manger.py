from aiogram import types

from src.core.engine import user_state
from src.telegram.keyboards.keyboards import create_main_menu, create_client_menu, create_report_menu
from src.telegram.states.title import Title

MAX_STATE_STACK_SIZE = 10

state_function_map = {
    'main_menu': create_main_menu,
    'client_menu': create_client_menu,
    'report_menu': create_report_menu
}


async def process_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data

    if data in state_function_map:
        await switch_state(user_id, data, callback_query.message)
    elif data == 'back':
        await go_back(callback_query)
    else:
        await callback_query.answer(f"Вы выбрали: {data}")


async def switch_state(user_id: int, new_state: str, message: types.Message):
    if user_id not in user_state:
        user_state[user_id] = []

    user_state[user_id].append(new_state)
    await check_and_trim_state_stack(user_id)

    markup = await state_function_map[new_state]()
    await message.bot.send_message(chat_id=message.chat.id, text="Выберите действие:", reply_markup=markup)
    await Title.start_action.set()


async def go_back(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id in user_state and user_state[user_id]:
        user_state[user_id].pop()
        if user_state[user_id]:
            if len(user_state[user_id]) > 1:
                previous_state = user_state[user_id][len(user_state[user_id])-1]
                markup = await state_function_map[previous_state]()
                await callback_query.message.bot.send_message(chat_id=callback_query.message.chat.id,
                                                              text="Выберите действие:", reply_markup=markup)
            else:
                markup = await state_function_map['main_menu']()
                await callback_query.message.bot.send_message(chat_id=callback_query.message.chat.id,
                                                              text="Вы вернулись в главное меню.", reply_markup=markup)
                await Title.start_action.set()
    else:
        markup = await state_function_map['main_menu']()
        await callback_query.message.bot.send_message(chat_id=callback_query.message.chat.id,
                                                      text="Вы вернулись в главное меню.", reply_markup=markup)
        await Title.start_action.set()
    await callback_query.answer()


async def check_and_trim_state_stack(user_id: int):
    if len(user_state[user_id]) > MAX_STATE_STACK_SIZE:
        user_state[user_id].pop(0)
