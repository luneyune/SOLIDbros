import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup

from intercomAPI import *

import config

# Инициализация бота
bot = telebot.TeleBot(config.BOT_TOKEN)

interAPI = IntercomAPI(config.DOM_API_TOKEN)

# Создание кнопки с запросом номера телефона
contact_button = KeyboardButton(text="Отправить номер", request_contact=True)

# Создание клавиатуры с кнопкой
reply_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
reply_keyboard.add(contact_button)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Нажмите кнопку, чтобы отправить свой номер телефона", reply_markup=reply_keyboard)

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

    # Отправляем номер обратно пользователю
    bot.send_message(message.chat.id, f"Спасибо! Ваш номер телефона: {user_phone_number}")


# Запуск бота
bot.polling(none_stop=True)