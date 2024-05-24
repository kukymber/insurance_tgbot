from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура главного меню."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(KeyboardButton("Клиент"), KeyboardButton("Отчет"))
    return markup


def get_client_action_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для выбора действий с клиентом."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Создать", "Изменить", "Найти", "Назад")
    return markup


def get_report_action_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для выбора действий с отчетами."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Выбрать период", "Отметить продленные", "Назад")
    return markup
