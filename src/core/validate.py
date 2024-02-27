from datetime import datetime
import re
from enum import Enum


class InsuranceInfoEnum(Enum):
    osago = "ОСАГО"
    mortgage = "Ипотека"
    selfinsurance = "Личное страхование"
    other = "Другой вид"


def validate_name(name: str):
    if not re.fullmatch(r'[А-Яа-яЁёA-Za-z]+', name):
        return False, "Имя должно содержать только буквы и не содержать пробелов."
    return True, name.strip()


def validate_phone(phone: str):
    if not re.fullmatch(r'\d{11}', phone):
        return False, "Номер телефона должен содержать 11 цифр."
    return True, phone


def validate_email(email: str):
    if not re.fullmatch(r'[^@]+@[^@]+\.[^@]+', email):
        return False, "Некорректный формат email."
    return True, email


def validate_date(date_str: str):
    try:
        date_obj = datetime.strptime(date_str, "%d.%m.%Y")
        if not (2015 <= date_obj.year <= 2050):
            raise ValueError("Год должен быть в диапазоне от 2015 до 2050.")
        return True, date_obj.date().isoformat()
    except ValueError as e:
        return False, f"Некорректная дата: {str(e)}"


