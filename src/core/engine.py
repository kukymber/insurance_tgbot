# engine.py
import logging
import os
from functools import wraps

import httpx
from aiogram import Bot, Dispatcher
from aiogram import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from dotenv import load_dotenv

from src.telegram.keyboards.keyboards import create_main_menu
from src.telegram.states.title import Title

load_dotenv()
TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_TOKEN: str = os.getenv('TELEGRAM_TOKEN')
API_URL: str = os.getenv('API_URL')
if not TELEGRAM_TOKEN:
    raise ValueError("Необходимо задать токен бота через переменную окружения TELEGRAM_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
storage = MemoryStorage()

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

user_state = {}


def start_bot() -> None:
    from src.telegram.handlers.handlers import register_handlers
    from src.telegram.start import send_to_admin
    register_handlers(dp)
    executor.start_polling(dp, on_startup=send_to_admin, skip_updates=True)


async def check_server_status():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_URL}/health")
            if response.status_code == 200 and response.json().get("status") == "ok":
                return True
            else:
                return False
        except httpx.HTTPStatusError as exc:
            print(f"HTTP error occurred: {exc}")
            return False
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting {exc.request.url!r}.")
            return False


def server_check_decorator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if await check_server_status():
            return await func(*args, **kwargs)
        else:
            message = kwargs.get('message') or (args[0] if args else None)
            if message:
                await message.answer("Сервер недоступен")
                await Title.start_action.set()
                markup = create_main_menu()
                await message.answer("Выберите действие:", reply_markup=markup)
            return None
    return wrapper
