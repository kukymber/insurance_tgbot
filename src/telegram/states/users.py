from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from src.core.engine import TELEGRAM_CHAT_ID, bot


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
    async def set_previous(cls, state: FSMContext, previous_state):
        """
        Сохраняем предыдущее состояние в контексте пользователя.
        """
        async with state.proxy() as data:
            data['previous_state'] = previous_state

    @classmethod
    async def go_back(cls, state: FSMContext):
        data = await state.get_data()
        if data:
            key_to_remove = data['previous_state'].split(':')[1]

            input_text = data.pop(key_to_remove, None)

            if input_text:

                await state.set_data(data)
                state_to_set = getattr(UserDataState, key_to_remove)
                await state_to_set.set()
                await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"Вы вводили - '{input_text}'")
            else:
                await state.finish()
        else:
            await state.finish()
