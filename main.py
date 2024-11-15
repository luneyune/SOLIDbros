import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup

from intercomAPI import *
from dbManager import *

import config

# Инициализация бота
bot = telebot.TeleBot(config.BOT_TOKEN)
interAPI = IntercomAPI(config.DOM_API_TOKEN)
dbManager = DBManager("users.db")

# Создание кнопки с запросом номера телефона
contact_button = KeyboardButton(text="Отправить номер", request_contact=True)

# Создание клавиатуры с кнопкой
reply_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
reply_keyboard.add(contact_button)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Нажмите кнопку, чтобы отправить свой номер телефона", reply_markup=reply_keyboard)


@bot.message_handler(commands=['locations'])
def get_user_locations(message):
    tenant_id = dbManager.read_tenant(message.from_user.id)[0]
    print(tenant_id)
    try:
        locations = interAPI.domo_apartment(tenant_id)
        bot.send_message(message.from_user.id, f"ID Ваших локаций: {locations}")
    except TenantDoesntExist:
        bot.send_message(message.from_user.id, f"У вас нет локаций...")
        return

# Обработчик текстовых сообщений
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    bot.send_message(message.from_user.id, message.text)

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    # Получаем номер телефона из сообщения
    user_phone_number = message.contact.phone_number[1:]

    try:
        tenant_id = interAPI.check_tenant(user_phone_number)
        bot.send_message(message.chat.id, f"Ваш tenant_id = {tenant_id}")
    except TenantDoesntExist:
        bot.send_message(message.chat.id, "Вы не зарегистрированы в нашей системе!")

    dbManager.write_tenant(message.from_user.id, tenant_id, user_phone_number)
    # Отправляем номер обратно пользователю
    bot.send_message(message.chat.id, f"Спасибо! Вы успешно вошли в систему!")


# Запуск бота
bot.polling(none_stop=True)
