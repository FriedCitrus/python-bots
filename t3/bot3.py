
import telebot
import requests


TOKEN = "8210010076:AAHLuBwF27_3kS6RkdlBluhof8cPMg4nDaI"
API_KEY = "a4e198dad358434d84f55be0286c1faa"
API_URL = f"https://openexchangerates.org/api/latest.json?app_id={API_KEY}"

bot = telebot.TeleBot(TOKEN)

def get_rates():
    try:
        response = requests.get(API_URL)
        data = response.json()
        return data["rates"]
    except Exception as e:
        print("Помилка при отриманні курсів", e)
        return None


def convert(amount, from_currency, to_currency):
    rates = get_rates()
    if not rates:
        return "Не вдалося отримати курси валют."

    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    if from_currency not in rates or to_currency not in rates:
        return f"Валюта {from_currency} або {to_currency} не підтримується."

    usd_amount = amount / rates[from_currency]  # конвертація в USD
    converted = usd_amount * rates[to_currency]
    return f"{amount} {from_currency} = {converted:.2f} {to_currency}"

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.strip()

    if text.lower() in ["/start", "/help"]:
        bot.reply_to(message,
                     "Введsnm запит у форматі:\n100 USD в EUR\n/rates - перегляд основних курсів.")

    elif text.lower() == "/rates":
        rates = get_rates()
        if rates:
            reply = (
                f"Основні курси:\n"
                f"1 USD = {rates['EUR']:.2f} EUR\n"
                f"1 USD = {rates['GBP']:.2f} GBP\n"
                f"1 USD = {rates['UAH']:.2f} UAH"
            )
            bot.reply_to(message, reply)
        else:
            bot.reply_to(message, "Не вдалося отримати курси валют.")

    else:
        try:
            parts = text.split()
            amount = float(parts[0])
            from_currency = parts[1]
            to_currency = parts[3]

            result = convert(amount, from_currency, to_currency)
            bot.reply_to(message, result)
        except Exception:
            bot.reply_to(message, "Невірний формат. Використовуйте: 100 USD в EUR")

bot.polling()
