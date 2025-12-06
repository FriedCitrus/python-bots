import telebot
import requests
from telebot import types

SERVICE_URL = "http://127.0.0.1:8000/api/v1/horoscope"

UA_TO_EN = {
    "овен": "aries", "телець": "taurus", "близнюки": "gemini", "рак": "cancer",
    "лев": "leo", "діва": "virgo", "терези": "libra", "скорпіон": "scorpio",
    "стрілець": "sagittarius", "козеріг": "capricorn", "водолій": "aquarius", "риби": "pisces"
}
ZODIAC_UA = [
    "Овен", "Телець", "Близнюки", "Рак", "Лев", "Діва",
    "Терези", "Скорпіон", "Стрілець", "Козеріг", "Водолій", "Риби"
]

bot = telebot.TeleBot(TOKEN)
user_sign = {}

@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for sign in ZODIAC_UA:
        markup.add(types.KeyboardButton(sign))
    bot.send_message(message.chat.id, "Обери знак зодіаку:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text and m.text.lower() in [s.lower() for s in ZODIAC_UA])
def choose_sign(message):
    ua = message.text.lower()
    en = UA_TO_EN.get(ua)
    user_sign[message.chat.id] = en
    bot.send_message(message.chat.id, f"Знак збережено: {message.text}. Напишіть /today або виберіть день: сьогодні/завтра/вчора.")

def fetch_horoscope(en_sign: str, day: str = "today") -> str:
    params = {"sign": en_sign, "day": day}
    try:
        r = requests.get(SERVICE_URL, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return data.get("horoscope", "Немає даних")
        else:
            return f"Помилка сервісу: {r.status_code}"
    except Exception:
        return "Не вдалося отримати гороскоп"

@bot.message_handler(commands=["today"])
def today(message):
    en = user_sign.get(message.chat.id)
    if not en:
        bot.send_message(message.chat.id, "Спочатку обери свій знак зодіаку.")
        return
    text = fetch_horoscope(en, "today")
    bot.send_message(message.chat.id, f"Гороскоп на сьогодні:\n{text}")

@bot.message_handler(commands=["help"])
def help_cmd(message):
    bot.send_message(message.chat.id, "Команди:\n/start – почати\n/today – гороскоп на сьогодні\n/help – допомога")

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ["сьогодні", "завтра", "вчора"])
def day_picker(message):
    day_map = {"сьогодні": "today", "завтра": "tomorrow", "вчора": "yesterday"}
    en = user_sign.get(message.chat.id)
    if not en:
        bot.send_message(message.chat.id, "Спочатку обери свій знак зодіаку.")
        return
    day_key = day_map[message.text.lower()]
    text = fetch_horoscope(en, day_key)
    bot.send_message(message.chat.id, f"Гороскоп на {message.text.lower()}:\n{text}")

bot.polling(none_stop=True)
