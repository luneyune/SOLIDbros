import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup

from intercomAPI import *
from dbManager import *
from sqlite_setup import *

import config

# Инициализация БД на случай первого запуска
db_setup()

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
    tenant = dbManager.read_tenant(message.from_user.id)
    if not tenant:
        bot.send_message(message.from_user.id, f"У вас нет локаций...")
        return
    tenant_id = tenant[0]
    try:
        locations = interAPI.tenant_apartments(tenant_id)
        bot.send_message(message.from_user.id, f"ID Ваших локаций: {locations}")
    except ValidationError:
        bot.send_message(message.from_user.id, f"У вас нет локаций...")
        return
    
@bot.message_handler(commands=['intercoms'])
def get_user_locations(message):
    tenant = dbManager.read_tenant(message.from_user.id)
    if not tenant:
        bot.send_message(message.from_user.id, f"У вас нет домофонов...")
        return
    tenant_id = tenant[0]
    try:
        locations = interAPI.tenant_apartments(tenant_id)
        intercoms = []
        for loc_id in locations:
            intercoms_for_loc = interAPI.apartment_intercoms(loc_id, tenant_id)
            intercoms += intercoms_for_loc

        bot.send_message(message.from_user.id, f"Ваши домофоны: {intercoms}")
    except ValidationError:
        bot.send_message(message.from_user.id, f"У вас нет локаций...")
        return

# Обработчик текстовых сообщений
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text[:4] == "open":
        tenant = dbManager.read_tenant(message.from_user.id)
        if not tenant:
            bot.send_message(message.from_user.id, f"У вас нет домофонов...")
            return
        tenant_id = tenant[0]
        inter_id = int(message.text[5:])
        is_open = interAPI.open_intercom(inter_id, tenant_id)
        if is_open:
            bot.send_message(message.from_user.id, f"Дверь успешно открыта")
        else:
            bot.send_message(message.from_user.id, f"Ошибка успешно открыта")
    
    elif message.text[:5] == "image":
        tenant = dbManager.read_tenant(message.from_user.id)
        if not tenant:
            bot.send_message(message.from_user.id, f"У вас нет домофонов...")
            return
        tenant_id = tenant[0]
        inter_id = int(message.text[6:])

        try:
            img = interAPI.intercom_image(inter_id, tenant_id)
        except ValidationError:
            bot.send_message(message.from_user.id, f"Этот домофон вам недоступен")

        bot.send_photo(message.from_user.id, img[0])


@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    # Получаем номер телефона из сообщения
    user_phone_number = message.contact.phone_number[1:]

    try:
        tenant_id = interAPI.check_tenant(user_phone_number)
        bot.send_message(message.chat.id, f"Ваш tenant_id = {tenant_id}")
    except ValidationError:
        bot.send_message(message.chat.id, "Вы не зарегистрированы в нашей системе!")
        return

    dbManager.write_tenant(message.from_user.id, tenant_id, user_phone_number)
    # Отправляем номер обратно пользователю
    bot.send_message(message.chat.id, f"Спасибо! Вы успешно вошли в систему!")


# Запуск бота
bot.polling(none_stop=True)
