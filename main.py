
import telebot

TOKEN = "8524077925:AAFIwESUQfOLzddFYLFLI3w1w0mrXec0CgM"
bot = telebot.TeleBot(TOKEN)

user_state = {}
order_data = {}

STATE_START = "start"
STATE_ORDER = "order"
STATE_ADDRESS = "address"
STATE_CONFIRM = "confirm"
STATE_FINISH = "finish"


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    user_state[user_id] = STATE_START

    bot.send_message(user_id, "Привіт! Я бот для замовлення холодних напоїв. Хочеш купити?")


@bot.message_handler(func=lambda m: True)
def dialog(message):
    user_id = message.chat.id
    text = message.text.lower()

    state = user_state.get(user_id, STATE_START)

    if state == STATE_START:
        order_data[user_id] = {"drink": None, "address": None}

        order_data[user_id]["drink"] = text
        bot.send_message(user_id, f"Ви бажаєте замовити {text}, правильно? (так/ні)")
        user_state[user_id] = STATE_CONFIRM

    elif state == STATE_CONFIRM:
        if text == "так":
            bot.send_message(user_id, "Гаразд, вкажіть адресу видачі напою")
            user_state[user_id] = STATE_ADDRESS

        elif text == "ні":
            bot.send_message(user_id, "Добре, який напій бажаєте?")
            user_state[user_id] = STATE_ORDER

        else:
            bot.send_message(user_id, "Будь ласка, відповідайте: так або ні.")

    elif state == STATE_ORDER:
        order_data[user_id]["drink"] = text
        bot.send_message(user_id, f"Ви бажаєте замовити {text}, правильно? (так/ні)")
        user_state[user_id] = STATE_CONFIRM

    elif state == STATE_ADDRESS:
        order_data[user_id]["address"] = text

        drink = order_data[user_id]["drink"]
        address = order_data[user_id]["address"]

        bot.send_message(
            user_id,
            f"Замовлення оформлено!\n"
            f"Напій: {drink}\n"
            f"Адреса видачі: {address}\n"
            f"Дякуємо за замовлення!"
        )

        user_state[user_id] = STATE_FINISH

    elif state == STATE_FINISH:
        bot.send_message(user_id, "Напишіть /start для нового замовлення.")
        user_state[user_id] = STATE_START


print("Бот запущено!")
bot.polling(none_stop=True)
ot.polling(none_stop=True)
