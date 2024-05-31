import os
import telebot
from telebot import types
from datetime import timedelta, datetime
from dotenv import load_dotenv
from search import search_flights, search_train, search_hotels
from city import city_code_search, city_search_c_code
from repair_text import repair_data, parse_date

# Загрузка переменных окружения из .env файла
load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')

if not API_TOKEN:
    raise ValueError("TELEGRAM_API_TOKEN is not set in environment variables")

bot = telebot.TeleBot(API_TOKEN)

# Словарь для хранения состояния пользователей
user_states = {}

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    send_main_menu(message)

@bot.callback_query_handler(func=lambda call: call.data == 'menu')
def send_menu(call):
    send_main_menu(call.message)

def send_main_menu(message):
    markup = types.InlineKeyboardMarkup()
    button_flights = types.InlineKeyboardButton(text='Найти авиабилеты', callback_data='search_flights')
    button_trains = types.InlineKeyboardButton(text='Найти билеты на поезд', callback_data='search_trains')
    button_hotels = types.InlineKeyboardButton(text='Найти отель', callback_data='search_hotels')
    markup.add(button_flights, button_trains, button_hotels)
    bot.send_message(message.chat.id, "Привет, я могу помочь с поиском билетов по России.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'search_flights')
def search_flights_handler(call):
    bot.answer_callback_query(call.id)
    user_states[call.message.chat.id] = {'state': 'waiting_fly_destination_city'}
    bot.send_message(call.message.chat.id, "Пожалуйста, напишите, куда вы хотите лететь.")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'waiting_fly_destination_city')
def handle_destination_city(message):
    user_data = user_states.get(message.chat.id, {})
    destination_city_code = (message.text)
    check_destination_city_code = city_code_search(message.text)
    if check_destination_city_code:
        user_data['destination_city'] = destination_city_code
        user_data['state'] = 'waiting_fly_departure_city'
        bot.send_message(message.chat.id, "Теперь напишите, из какого города вы хотите вылететь.")
    else:
        markup = types.InlineKeyboardMarkup()
        text = "Не удалось найти указанный город. Попробуйте снова, или можете вернуться в стартовое меню."
        button_back_menu = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')
        markup.add(button_back_menu)
        bot.send_message(message.chat.id, text, reply_markup=markup)
        

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'waiting_fly_departure_city')
def handle_departure_city(message):
    user_data = user_states.get(message.chat.id, {})
    departure_city_code = (message.text)
    check_departure_city_code = city_code_search(message.text)
    if check_departure_city_code:
        user_data['departure_city'] = departure_city_code
        user_data['state'] = 'waiting_fly_date'
        bot.send_message(message.chat.id, f"Введите дату вылета из {user_data['departure_city']} в {user_data['destination_city']}.")
    else:
        markup = types.InlineKeyboardMarkup()
        text = "Не удалось найти указанный город. Попробуйте снова, или можете вернуться в стартовое меню."
        button_back_menu = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')
        markup.add(button_back_menu)
        bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'waiting_fly_date')
def handle_date(message):
    user_data = user_states.get(message.chat.id, {})
    user_data['state'] = 'ready_for_search'
    origin = city_code_search(user_data['departure_city'])
    destination = city_code_search(user_data['destination_city'])
    departure_date = parse_date(message.text) 

    flights = search_flights(origin, destination, departure_date)
    if flights:
        text = "Предлагаю вам эту подборку из рейсов:\n"
        count_flights = 0
        for i in flights:
            count_flights += 1
            text += f"{count_flights}. Рейс: {i['origin_airport']}-{i['destination_airport']}\n"
            text += f"Время отправления: {i['departure_at'][11:19]}\n"
            text += f"Цена: {i['price']} руб.\n\n"
            if count_flights >= 3:
                break

        text += "\n\n\n Для того, чтобы подробнее узнать о билетах на самолет, нажмите на кнопку 'Перейти на сайт'\n\n\n"
        departure_date = departure_date.replace("-", "")
        url_flights = f"https://www.aviasales.ru/search/{origin}{departure_date[6:8]}{departure_date[4:6]}{destination}1"

        markup = types.InlineKeyboardMarkup()
        button_flights_result = types.InlineKeyboardButton(text='Перейти на сайт', url=url_flights)
        button_back_menu = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')
        markup.add(button_flights_result, button_back_menu)
        bot.send_message(message.chat.id, text, reply_markup=markup)
    else:
        markup = types.InlineKeyboardMarkup()
        text = "К сожалению, рейсы не найдены. Попробуйте изменить параметры поиска, или вернуться в стартовое меню."
        button_back_menu = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')
        markup.add(button_back_menu)
        bot.send_message(message.chat.id, text, reply_markup=markup)

        

@bot.callback_query_handler(func=lambda call: call.data == 'search_trains')
def search_flights_handler(call):
    bot.answer_callback_query(call.id)
    user_states[call.message.chat.id] = {'state': 'waiting_ride_destination_city'}
    bot.send_message(call.message.chat.id, "Пожалуйста, напишите, куда вы хотите поехать.")


@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'waiting_ride_destination_city')
def handle_destination_city(message):
    user_data = user_states.get(message.chat.id, {})
    destination_city_code = (message.text)
    check_destination_city_code = city_search_c_code(message.text)
    if check_destination_city_code:
        user_data['destination_city'] = destination_city_code
        user_data['state'] = 'waiting_ride_departure_city'
        bot.send_message(message.chat.id, "Теперь напишите, из какого города вы хотите выехать.")
    else:
        markup = types.InlineKeyboardMarkup()
        text = "Не удалось найти указанный город. Попробуйте снова, или вернитесь в стартовое меню."
        button_back_menu = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')
        markup.add(button_back_menu)
        bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'waiting_ride_departure_city')
def handle_departure_city(message):
    user_data = user_states.get(message.chat.id, {})
    departure_city_code = (message.text)
    check_departure_city_code = city_search_c_code(message.text)
    if check_departure_city_code:
        user_data['departure_city'] = departure_city_code
        user_data['state'] = 'waiting_ride_date'
        bot.send_message(message.chat.id, f"Введите дату выезда из {user_data['departure_city']} в {user_data['destination_city']}.")
    else:
        markup = types.InlineKeyboardMarkup()
        text = "Не удалось найти указанный город. Попробуйте снова, или вернитесь в стартовое меню."
        button_back_menu = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')
        markup.add(button_back_menu)
        bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'waiting_ride_date')
def handle_date(message):
    user_data = user_states.get(message.chat.id, {})
    user_data['state'] = 'ready_for_search'
    origin = city_search_c_code(user_data['departure_city'])
    destination = city_search_c_code(user_data['destination_city'])
    departure_date = parse_date(message.text)  

    train = search_train(origin, destination, departure_date)
    if train:
        text = "Могу предложить вам такой вариант:\n"
        train_t = train.get("segments")
        if train_t and len(train_t) > 0:
            train_t = train_t[0]
            date_str = train_t["departure"][:10]
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            p_time = date_obj.strftime("%d-%m-%Y")
            text += f'Поезд {train_t["thread"]["number"]}, {train_t["thread"]["title"]}\n'
            text += f'Отправление: {p_time} в {train_t["departure"][11:19]} по времени города отбытия.\n\n'
            text += "Для того, чтобы подробнее узнать о билетах на поезд, нажмите на кнопку 'Перейти на сайт'\n\n"

            departure_date_formatted = departure_date.replace("-", "")
            url_train = f"https://rasp.yandex.ru/search/?fromId={origin}&toId={destination}&when={departure_date}"

            markup = types.InlineKeyboardMarkup()
            button_train_result = types.InlineKeyboardButton(text='Перейти на сайт', url=url_train)
            button_back_menu = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')
            markup.add(button_train_result, button_back_menu)
            bot.send_message(message.chat.id, text, reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "К сожалению, рейсы не найдены. Попробуйте изменить параметры поиска.")
    else:
        markup = types.InlineKeyboardMarkup()
        text = "К сожалению, рейсы не найдены. Попробуйте изменить параметры поиска, или вернитесь в стартовое меню."
        button_back_menu = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')
        markup.add(button_back_menu)
        bot.send_message(message.chat.id, text, reply_markup=markup)




@bot.callback_query_handler(func=lambda call: call.data == 'search_hotels')
def search_flights_handler(call):
    bot.answer_callback_query(call.id)
    user_states[call.message.chat.id] = {'state': 'waiting_hotel_city'}
    bot.send_message(call.message.chat.id, "В каком городе собираетесь остановиться?")


@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'waiting_hotel_city')
def handle_destination_city(message):
    user_data = user_states.get(message.chat.id, {})
    hotel_city_code = (message.text)
    check_hotel_city_code = city_code_search(message.text)
    if check_hotel_city_code:
        user_data['hotel_city'] = hotel_city_code
        user_data['state'] = 'hotel_data_in'
        bot.send_message(message.chat.id, "С какого числа вы бы хотели забронировать отель?")
    else:
        markup = types.InlineKeyboardMarkup()
        text = "Не удалось найти указанный город. Попробуйте снова, или вернитесь в стартовое меню."
        button_back_menu = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')
        markup.add(button_back_menu)
        bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'hotel_data_in')
def handle_destination_city(message):
    user_data = user_states.get(message.chat.id, {})
    hotel_data_in = parse_date(message.text)
    if hotel_data_in:
        user_data['hotel_data_in'] = hotel_data_in
        user_data['state'] = 'hotel_data_out'
        bot.send_message(message.chat.id, "Какого числа вы планируете уехать из отеля?")
    else:
        markup = types.InlineKeyboardMarkup()
        text = "Не удалось распознать дату, попробуйте ещё раз, или вернитесь в стартовое меню."
        button_back_menu = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')
        markup.add(button_back_menu)
        bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'hotel_data_out')
def handle_date(message):
    user_data = user_states.get(message.chat.id, {})
    user_data['state'] = 'ready_for_search'
    city_hotel = city_code_search(user_data['hotel_city'])
    hotel_data_in = user_data['hotel_data_in']
    hotel_data_out = parse_date(message.text)

    if not hotel_data_in:
        bot.send_message(message.chat.id, "Неверный формат даты. Пожалуйста, введите дату ещё раз")
        return

    hotels = search_hotels(city_hotel, hotel_data_in, hotel_data_out)
    if hotels:
        text = "Предлагаю вам эту подборку из отелей:\n"
        count_hotels = 0
        for i in hotels:
            count_hotels += 1
            text += str(count_hotels) + ". " + i['hotelName'] + ", Звёзды: " + str(i['stars'])\
                    + ', Средняя цена проживания: ' + str(i['priceAvg']) + " руб\n\n"
        text += "\n\n\nДля того, чтобы подробнее узнать об отелях, нажмите на кнопку 'Перейти на сайт'\n\n\n"

        url_hotels = f"https://search.hotellook.com/hotels?=1&adults=1&checkIn={hotel_data_in}&checkOut={hotel_data_out}&currency=rub&destination={city_hotel}&language=ru"

        markup = types.InlineKeyboardMarkup()
        button_hotels_result = types.InlineKeyboardButton(text='Перейти на сайт', url=url_hotels)
        button_back_menu = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')
        markup.add(button_hotels_result, button_back_menu)
        bot.send_message(message.chat.id, text, reply_markup=markup)
    else:
        markup = types.InlineKeyboardMarkup()
        text = "К сожалению, отели не найдены. Попробуйте изменить параметры поиска, или вернитесь в стартовое меню."
        button_back_menu = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')
        markup.add(button_back_menu)
        bot.send_message(message.chat.id, text, reply_markup=markup)



# Запуск бота
bot.polling()
