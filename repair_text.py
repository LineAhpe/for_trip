from datetime import datetime, timedelta
import re

# Перевод месяцев с русского на английский
month_translation = {
    'января': 'January', 'февраля': 'February', 'марта': 'March',
    'апреля': 'April', 'мая': 'May', 'июня': 'June',
    'июля': 'July', 'августа': 'August', 'сентября': 'September',
    'октября': 'October', 'ноября': 'November', 'декабря': 'December',
    'январь': 'January', 'февраль': 'February', 'март': 'March',
    'апрель': 'April', 'май': 'May', 'июнь': 'June',
    'июль': 'July', 'август': 'August', 'сентябрь': 'September',
    'октябрь': 'October', 'ноябрь': 'November', 'декабрь': 'December'
}

def parse_date(date_str):
    date_str = date_str.replace('.', '-')
    date_str = date_str.strip().lower()
    
    # Проверяем на специальные случаи
    if date_str == "сегодня":
        return datetime.now().strftime('%Y-%m-%d')
    elif date_str == "завтра":
        return (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    elif date_str == "послезавтра":
        return (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
    
    # Проверяем формат yyyy-mm-dd
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_str  # Уже в правильном формате
    except ValueError:
        pass
    
    # Проверяем формат dd-mm-yyyy
    try:
        date_obj = datetime.strptime(date_str, '%d-%m-%Y')
        return date_obj.strftime('%Y-%m-%d')
    except ValueError:
        pass
    
    # Обрабатываем формат "день месяц"
    parts = date_str.split()
    if len(parts) != 2:
        return None

    day, month = parts
    
    # Переводим русский месяц на английский
    month_en = month_translation.get(month)
    if not month_en:
        return None
    
    # Текущий год
    current_year = datetime.now().year
    
    # Форматируем строку в формате 'день месяц год'
    date_format = f"{day} {month_en} {current_year}"
    
    # Преобразуем строку в объект datetime
    try:
        date_obj = datetime.strptime(date_format, '%d %B %Y')
        current_date = datetime.now()
        
        # Проверяем, прошла ли эта дата в текущем году
        if date_obj < current_date:
            date_obj = datetime.strptime(f"{day} {month_en} {current_year + 1}", '%d %B %Y')
        
        # Возвращаем дату в формате yyyy-mm-dd
        return date_obj.strftime('%Y-%m-%d')
    except ValueError:
        return None
