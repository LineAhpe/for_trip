from datetime import datetime, timedelta
import datetime
import re
from fuzzywuzzy import process

def repair_data(data_value):
    now = datetime.now()
    if 'day' in data_value:
        if data_value['day_is_relative']:
            now = now + timedelta(days=int(data_value['day']))
        else:
            now = now.replace(day=int(data_value['day']))

    if "month" in data_value:
        month_p = int(data_value['month'])
        if data_value['month_is_relative']:
            if month_p + now.month > 12:
                now = now.replace(year=month_p//12+now.year)
                now = now.replace(month=month_p%12+now.month)
            else:
                now = now.replace(month=month_p+now.month)
        else:
            now = now.replace(month=month_p)
    if "year" in data_value:
        if data_value['year_is_relative']:
            now = now.replace(year=int(data_value['year']) + now.year)
        else:
            now = now.replace(year=int(data_value['year']))

    data = now.strftime('%Y-%m-%d')
    return data

# Словарь для перевода русских названий месяцев на английские
month_translation = {
    'января': 'January',
    'февраля': 'February',
    'марта': 'March',
    'апреля': 'April',
    'мая': 'May',
    'июня': 'June',
    'июля': 'July',
    'августа': 'August',
    'сентября': 'September',
    'октября': 'October',
    'ноября': 'November',
    'декабря': 'December'
}

def parse_date(date_str):
    # Разделяем строку на день и месяц
    parts = date_str.split()
    if len(parts) != 2:
        return "Некорректная дата"

    day, month = parts
    
    # Переводим русский месяц на английский
    month_en = month_translation.get(month.lower())
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
        return None
