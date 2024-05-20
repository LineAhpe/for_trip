import os
import telebot
import logging
from dotenv import load_dotenv
from tools import get_daily_horoscope  # Assuming tools.py is in the same directory

# Load environment variables from .env file
load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')

if not API_TOKEN:
    raise ValueError("TELEGRAM_API_TOKEN is not set in environment variables")

bot = telebot.TeleBot(API_TOKEN)

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Привет, как дела?")


@bot.message_handler(commands=['horoscope'])
def sign_handler(message):
    bot.send_message(message.chat.id, "Команда /horoscope получена")
    text = "What's your zodiac sign?\nChoose one: *Aries*, *Taurus*, *Gemini*, *Cancer,* *Leo*, *Virgo*, *Libra*, *Scorpio*, *Sagittarius*, *Capricorn*, *Aquarius*, and *Pisces*."
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, day_handler)


def day_handler(message):
    try:
        sign = message.text.strip()
        bot.send_message(message.chat.id, f"Вы выбрали знак: {sign}")
        text = "What day do you want to know?\nChoose one: *TODAY*, *TOMORROW*, *YESTERDAY*, or a date in format YYYY-MM-DD."
        sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
        bot.register_next_step_handler(sent_msg, fetch_horoscope, sign.capitalize())
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}")


def fetch_horoscope(message, sign):
    day = message.text
    horoscope = get_daily_horoscope(sign, day)
    data = horoscope["data"]
    horoscope_message = f'*Horoscope:* {data["horoscope_data"]}\n*Sign:* {sign}\n*Day:* {data["date"]}'
    bot.send_message(message.chat.id, "Here's your horoscope!")
    bot.send_message(message.chat.id, horoscope_message, parse_mode="Markdown")


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)


bot.infinity_polling()
