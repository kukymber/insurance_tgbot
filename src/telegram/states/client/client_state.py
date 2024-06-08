from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from src.core.engine import bot
from src.telegram.keyboards.keyboards import create_main_menu
from src.telegram.states.title import Title


class UserDataState(StatesGroup):
    user_id = State()
    action = State()
    first_name = State()
    middle_name = State()
    last_name = State()
    phone = State()
    email = State()
    time_insure_end = State()
    polis_type = State()
    process_description = State()

    @classmethod
    async def set_client_previous(cls, state: FSMContext, previous_client_state):
        """
        Сохраняем предыдущее состояние в контексте пользователя.
        """
        async with state.proxy() as data:
            if 'previous_client_states' not in data:
                data['previous_client_states'] = []
            data['previous_client_states'].append(previous_client_state)

    @classmethod
    async def go_back(cls, callback_query: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            if 'previous_client_states' in data and data['previous_client_states']:
                previous_client_state = data['previous_client_states'].pop()
                key_to_remove = previous_client_state.split(':')[1]

                input_text = data.pop(key_to_remove, None)

                if input_text:
                    await state.set_data(data)
                    state_to_set = getattr(UserDataState, key_to_remove)
                    await state_to_set.set()
                    await bot.send_message(chat_id=callback_query.from_user.id, text=f"Вы вводили - '{input_text}'")
                else:
                    await state.finish()
            else:
                await state.finish()
                markup = create_main_menu()
                await bot.send_message(chat_id=callback_query.from_user.id, text="Вы вернулись в главное меню.",
                                       reply_markup=markup)
                await Title.start_action.set()
        await callback_query.answer()
