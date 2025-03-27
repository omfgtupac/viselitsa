import telebot
from telebot import types
from config import TOKEN, keys
from extensions import ConvertionException, CryptoConverter

bot = telebot.TeleBot(TOKEN)


user_data = {}


@bot.message_handler(commands=["start", "help"])
def help(message: telebot.types.Message):
    markup = types.InlineKeyboardMarkup()
    button_usd = types.InlineKeyboardButton(text="USD", callback_data="currency_USD")
    button_eur = types.InlineKeyboardButton(text="EUR", callback_data="currency_EUR")
    button_rub = types.InlineKeyboardButton(text="RUB", callback_data="currency_RUB")
    markup.add(button_usd, button_eur, button_rub)

    text = ("Чтобы начать работу, выберите валюту для конвертации или введите команду боту в следующем формате:\n"
            "<имя валюты> <в какую валюту перевести> <количество переводимой валюты>\n"
            "Увидеть список всех доступных валют: /values")
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(commands=["values"])
def values(message: telebot.types.Message):
    text = "Доступные валюты: "
    for key in keys.keys():
        text = "\n".join((text, key,))
    bot.reply_to(message, text)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.data.startswith("currency_"):
            currency = call.data.split("_")[1]
            user_data[call.message.chat.id] = {"quote": currency}

            markup = types.InlineKeyboardMarkup()
            button_usd = types.InlineKeyboardButton(text="USD", callback_data=f"target_currency_USD")
            button_eur = types.InlineKeyboardButton(text="EUR", callback_data=f"target_currency_EUR")
            button_rub = types.InlineKeyboardButton(text="RUB", callback_data=f"target_currency_RUB")
            markup.add(button_usd, button_eur, button_rub)

            bot.send_message(call.message.chat.id,
                             f"Вы выбрали {currency}. Теперь выберите валюту, в которую хотите конвертировать:",
                             reply_markup=markup)
    except Exception as e:
        bot.reply_to(call.message, f"Не удалось обработать команду \n{e}")

    if call.data.startswith("target_currency_"):
        try:
            base = call.data.split("_")[2]
            user_data[call.message.chat.id]["base"] = base

            bot.send_message(call.message.chat.id, "Теперь введите количество:")
            bot.register_next_step_handler(call.message, get_amount)
        except Exception as e:
            bot.reply_to(call.message, f"Не удалось обработать команду \n{e}")

def get_amount(message: telebot.types.Message):
    try:
        amount = message.text

        amount = amount.replace(" ", "").replace(",", ".")

        try:
            amount = float(amount)
        except ValueError:
            raise ConvertionException("Количество должно быть числом. Пожалуйста, введите число.")

        chat_id = message.chat.id
        quote = user_data[chat_id]["quote"]
        base = user_data[chat_id]["base"]

        total_base = CryptoConverter.get_price(quote, base, amount)
        text = f"Цена {amount} {quote} в {base} - {total_base * float(amount)}"
        bot.send_message(chat_id, text)

        user_data.pop(chat_id, None)
    except ConvertionException as e:
        bot.reply_to(message, f"Ошибка пользователя \n{e}")
    except Exception as e:
        bot.reply_to(message, f"Не удалось обработать команду \n{e}")

@bot.message_handler(content_types=["text"])
def convert(message: telebot.types.Message):
    try:
        if message.chat.id in user_data:
            return

        values = message.text.split(" ")

        if len(values) != 3:
            raise ConvertionException("Слишком много параметров")

        quote, base, amount = values
        total_base = CryptoConverter.get_price(quote, base, amount)
    except ConvertionException as e:
        bot.reply_to(message, f"Ошибка пользователя \n{e}")
    except Exception as e:
        bot.reply_to(message, f"Не удалось обработать команду \n{e}")
    else:
        text = f"Цена {amount} {quote} в {base} - {total_base * float(amount)}"
        bot.send_message(message.chat.id, text)

bot.polling()