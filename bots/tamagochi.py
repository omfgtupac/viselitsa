import telebot
import requests
from config import TOKEN


bot = telebot.TeleBot(TOKEN)


class CatPet:
    def __init__(self, name, breed):
        self.name = name
        self.breed = breed
        self.hunger = 50
        self.happiness = 50

    def feed(self):
        self.hunger = max(0, self.hunger - 20)
        self.happiness = min(100, self.happiness + 5)

    def play(self):
        self.happiness = min(100, self.happiness + 20)
        self.hunger = min(100, self.hunger + 5)

    def get_status(self):
        return f"Имя: {self.name}\nПорода: {self.breed}\nГолод: {self.hunger}\nСчастье: {self.happiness}"


pets = {}


def get_cat_breeds():
    url = 'https://catfact.ninja/breeds'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('data', [])
    return []


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Добро пожаловать в Tamagotchi! Введите имя вашего кота:")
    bot.register_next_step_handler(message, set_name)


def set_name(message):
    chat_id = message.chat.id
    pet_name = message.text
    breeds = get_cat_breeds()
    if breeds:
        breeds_list = "\n".join([f"{breed['breed']}" for breed in breeds])
        bot.send_message(chat_id, f"Выберите породу кота из списка:\n{breeds_list}")
        bot.register_next_step_handler(message, set_breed, pet_name, breeds)
    else:
        bot.send_message(chat_id, "Не удалось загрузить список пород. Попробуйте позже.")


def set_breed(message, pet_name, breeds):
    chat_id = message.chat.id
    breed_name = message.text
    our_breed = next((breed for breed in breeds if breed['breed'] == breed_name), None)
    if our_breed:
        pets[chat_id] = CatPet(pet_name, our_breed)
        bot.send_message(chat_id, f"Ваш кот {pet_name} породы {our_breed['breed']} создан!\n"
                                  f"Страна этой породы - {our_breed['country']}. Присхождение - {our_breed['origin']}. Шерсть {our_breed['coat']}, а окрас {our_breed['pattern']}.\n"
                                  f"Используйте /menu для управления.")
    else:
        bot.send_message(chat_id, "Порода не найдена. Попробуйте снова. Необходимо выбрать породу из списка.")
        bot.register_next_step_handler(message, set_breed, pet_name, breeds)



@bot.message_handler(commands=['menu'])
def menu(message):
    chat_id = message.chat.id
    if chat_id in pets:
        pet = pets[chat_id]
        bot.send_message(chat_id, "Используйте команды:\n" 
                                  f"/feed - Покормить\n/play - Поиграть\n/status - Статус\n/fact - Факт о коте")


@bot.message_handler(commands=['feed'])
def feed(message):
    chat_id = message.chat.id
    if chat_id in pets:
        pet = pets[chat_id]
        pet.feed()
        bot.send_message(chat_id, f"Вы покормили {pet.name}!\n{pet.get_status()}")
    else:
        bot.send_message(chat_id, "Сначала создайте кота с помощью /start.")


@bot.message_handler(commands=['play'])
def play(message):
    chat_id = message.chat.id
    if chat_id in pets:
        pet = pets[chat_id]
        pet.play()
        bot.send_message(chat_id, f"Вы поиграли с {pet.name}!\n{pet.get_status()}")
    else:
        bot.send_message(chat_id, "Сначала создайте кота с помощью /start.")


@bot.message_handler(commands=['status'])
def status(message):
    chat_id = message.chat.id
    if chat_id in pets:
        pet = pets[chat_id]
        bot.send_message(chat_id, pet.get_status())
    else:
        bot.send_message(chat_id, "Сначала создайте кота с помощью /start.")


@bot.message_handler(commands=['fact'])
def fact(message):
    chat_id = message.chat.id
    response = requests.get('https://catfact.ninja/fact')
    if response.status_code == 200:
        fact_text = response.json()['fact']
        bot.send_message(chat_id, f"Рандомный факт о коте: {fact_text}")
    else:
        bot.send_message(chat_id, "Не удалось получить факт о коте.")


if __name__ == '__main__':
    bot.polling()