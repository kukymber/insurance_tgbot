from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def create_main_menu() -> InlineKeyboardMarkup:
    """
    Создает главное меню с кнопками для перехода в меню клиента и меню отчетов.
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("Меню клиента", callback_data='client_menu'))
    keyboard.add(InlineKeyboardButton("Меню отчетов", callback_data='report_menu'))
    return keyboard


async def create_client_menu() -> InlineKeyboardMarkup:
    """
    Создает меню клиента с кнопками для создания, изменения, поиска данных, а также кнопками для перехода назад и в главное меню.
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("Создать", callback_data='create'))
    keyboard.add(InlineKeyboardButton("Изменить", callback_data='edit'))
    keyboard.add(InlineKeyboardButton("Найти", callback_data='find'))
    keyboard.add(InlineKeyboardButton("Назад", callback_data='back'))
    keyboard.add(InlineKeyboardButton("Главное меню", callback_data='main_menu'))
    return keyboard


async def create_report_menu() -> InlineKeyboardMarkup:
    """
    Создает меню отчетов с кнопками для создания отчета за период, отметки продления, а также кнопками для перехода назад и в главное меню.
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("Отчет за период", callback_data='period_report'))
    keyboard.add(InlineKeyboardButton("Отметить продление", callback_data='renew_report'))
    keyboard.add(InlineKeyboardButton("Назад", callback_data='back'))
    keyboard.add(InlineKeyboardButton("Главное меню", callback_data='main_menu'))
    return keyboard


async def get_step_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой для перехода назад на предыдущий шаг.
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("предыдущий шаг", callback_data='предыдущий шаг'))
    return keyboard