import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

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

# Создание клавиатуры с функциями
actions_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
intercoms_button = KeyboardButton(text="Просмотреть домофоны")
actions_keyboard.add(intercoms_button)

def get_intercoms(user_id):
    tenant = dbManager.read_tenant(user_id)
    if not tenant:
        bot.send_message(user_id, f"У вас нет домофонов...")
        return []
    tenant_id = tenant[0]
    try:
        locations = interAPI.tenant_apartments(tenant_id)
        intercoms = []
        for loc_id in locations:
            intercoms_for_loc = interAPI.apartment_intercoms(loc_id, tenant_id)
            intercoms += intercoms_for_loc
        return intercoms
    except ValidationError:
        return []

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

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    tenant = dbManager.read_tenant(call.message.chat.id)
    if not tenant:
        bot.send_message(call.message.chat.id, f"У вас нет домофонов...")
        return
    tenant_id = tenant[0]

    if call.data.isdigit():
        inter_id = int(call.data)
        image = interAPI.intercom_image(inter_id, tenant_id)

        inter_actions_keyboard = InlineKeyboardMarkup(row_width=2)
        open_button = InlineKeyboardButton(text="Открыть", callback_data=f"open {inter_id}")
        refresh_button = InlineKeyboardButton(text="Обновить", callback_data=inter_id)
        inter_actions_keyboard.row(open_button, refresh_button)

        bot.send_photo(call.message.chat.id, image[0], reply_markup=inter_actions_keyboard)

    if call.data[:4] == "open":
        inter_id = int(call.data[5:])
        is_open = interAPI.open_intercom(inter_id, tenant_id)
        if is_open:
            bot.send_message(call.message.chat.id, f"Дверь успешно открыта")
        else:
            bot.send_message(call.message.chat.id, f"Ошибка, нельзя открыть дверь")

# Обработчик текстовых сообщений
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Просмотреть домофоны":
        intercom_keyboard = InlineKeyboardMarkup()
        
        user_id = message.from_user.id
        intercoms = get_intercoms(user_id)

        for inter in intercoms:
            button = InlineKeyboardButton(text=inter[1], callback_data=inter[0])
            intercom_keyboard.add(button)
        
        bot.send_message(message.chat.id, "ㅤㅤㅤГлавное меню домофоновㅤ", reply_markup=intercom_keyboard)

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
    bot.send_message(message.chat.id, f"Спасибо! Вы успешно вошли в систему!")
    bot.send_message(message.chat.id, text="Выберите действие", reply_markup=actions_keyboard)


# Запуск бота
bot.polling(none_stop=True)
