import os
from functools import wraps

import httpx
from dotenv import load_dotenv

from src.telegram.keyboards.keyboards import create_main_menu
from src.telegram.states.title import Title

load_dotenv()
API_URL: str = os.getenv('API_URL')


async def check_server_status() -> bool:
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
