import requests
from datetime import timedelta
import json
from bs4 import BeautifulSoup
from googletrans import Translator
from datetime import datetime, timedelta
import random
from random import randint
from transliterate import translit

# Поиск Авиабилетов
def search_flights(origin, destination, departure_date):
    url = 'https://api.travelpayouts.com/aviasales/v3/prices_for_dates?'
    
    # API parameters
    params ={
        'origin': origin,
        'destination': destination,
        'depart_date': departure_date,
        'sorting':'price',
        'token': 'fc248c79dce9c306cef7a60618753323'
    }

    # Send request to API
    response = requests.get(url, params=params).json()
    data = response['data']
    return data

# Поиск ЖД Билетов
def search_train(origin, destination, departure_date):
    url = "https://api.rasp.yandex.net/v3.0/search/"

    # Параметры запроса
    params = {
        "apikey": "f5b9a737-a5cf-4a05-b486-39e6dea9e2d3", # Вставьте свой API-ключ
        "from": origin, # Введите код станции отправления
        "to": destination, # Введите код станции прибытия
        "date":departure_date,
        "transport_types": "train"
    }

    # Отправляем запрос и получаем ответ в формате JSON
    response = requests.get(url, params=params).json()

    # Извлекаем данные о найденных поездах
    return response

# Поиск Отелей
def search_hotels(destination, checkin_date, checkout_date):
    # API URL для поиска отелей на TripAdvisor
    url = "http://engine.hotellook.com/api/v2/cache.json"

    # Параметры запроса
    params = {
        'location':destination, # Москва
        "currency": "rub",
        "checkIn": checkin_date,
        "checkOut":checkout_date,
        "adultsCount": 2,
        "roomsCount": 1,
        "lang": "ru",
        'token': 'fc248c79dce9c306cef7a60618753323'
    }

    # Заголовки запроса
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    # Отправляем запрос и получаем ответ в формате JSON
    response = requests.get(url, params=params, headers=headers).json()
    # Извлекаем данные о найденных отелях
    return response
