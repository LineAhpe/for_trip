from datetime import datetime, timedelta
import datetime
import re
from fuzzywuzzy import process


# Перевод месяцев с русского на английский
month_translation = {
    'января': 'January', 'февраля': 'February', 'марта': 'March',
    'апреля': 'April', 'мая': 'May', 'июня': 'June',
    'июля': 'July', 'августа': 'August', 'сентября': 'September',
    'октября': 'October', 'ноября': 'November', 'декабря': 'December'
}

def parse_date(date_str):
    date_str = date_str.strip().lower()
    
    # Проверяем на специальные случаи
    if date_str == "сегодня":
        return datetime.datetime.now().strftime('%Y-%m-%d')
    elif date_str == "завтра":
        return (datetime.datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    elif date_str == "послезавтра":
        return (datetime.datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
    
    # Проверяем формат yyyy-mm-dd
    try:
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        return date_str  # Уже в правильном формате
    except ValueError:
        pass
    
    # Проверяем формат dd-mm-yyyy
    try:
        date_obj = datetime.datetime.strptime(date_str, '%d-%m-%Y')
        return date_obj.strftime('%Y-%m-%d')
    except ValueError:
        pass
    
    # Обрабатываем формат "день месяц"
    parts = date_str.split()
    if len(parts) != 2:
        return "Некорректная дата"

    day, month = parts
    
    # Переводим русский месяц на английский
    month_en = month_translation.get(month)
    if not month_en:
        return "Некорректная дата"
    
    # Текущий год
    current_year = datetime.datetime.now().year
    
    # Форматируем строку в формате 'день месяц год'
    date_format = f"{day} {month_en} {current_year}"
    
    # Преобразуем строку в объект datetime
    try:
        date_obj = datetime.datetime.strptime(date_format, '%d %B %Y')
        # Возвращаем дату в формате yyyy-mm-dd
        return date_obj.strftime('%Y-%m-%d')
    except ValueError:
        return "Некорректная дата"
