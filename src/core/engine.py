import logging
import os

from aiogram import Bot, Dispatcher
from aiogram import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from dotenv import load_dotenv

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



