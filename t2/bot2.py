import telebot
import requests
from datetime import datetime

TOKEN = "8210010076:AAHLuBwF27_3kS6RkdlBluhof8cPMg4nDaI"

API_KEY = "f4d36a518b26701fcd89eea2d45e67f2"

bot = telebot.TeleBot(TOKEN)

def trans(text):
    mapping = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g', 'д': 'd',
        'е': 'e', 'є': 'ye', 'ж': 'zh', 'з': 'z', 'и': 'y', 'і': 'i',
        'ї': 'yi', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
        'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
        'ю': 'yu', 'я': 'ya', 'ь': '', '’': '', "'": ''
    }
    result = ''
    for char in text.lower():
        result += mapping.get(char, char)
    return result.capitalize()

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=ua"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"].capitalize()
        wind = data["wind"]["speed"]
        date = datetime.now().strftime("%d.%m.%Y")
        return f"Погода в {city.capitalize()} на {date}:\nТемпература: {temp}°C\nОпис: {description}\nШвидкість вітру: {wind} м/с"
    elif response.status_code == 404:
        return "Місто не знайдено. Спробуйте ввести назву англійською або перевірте написання."
    else:
        return f"Помилка API: {response.status_code}"

@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(message, "Введіть назву міста англійською чи українською для прогнозу погоди.")

@bot.message_handler(func=lambda message: True)
def weather_request(message):
    city_ua = message.text.strip()
    city_en = trans(city_ua)
    forecast = get_weather(city_en)
    bot.reply_to(message, forecast)

bot.polling(none_stop=True)
