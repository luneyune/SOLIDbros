import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request, jsonify
import threading
import bcrypt

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

api_app = Flask(__name__)

def get_tenant_or_send_error(tg_id):
    tenant = dbManager.read_tenant(tg_id)
    if not tenant:
        bot.send_message(tg_id, f"У вас нет домофонов...")
        return None
    tenant_id = tenant[0]
    return tenant_id

def apartments_menu(tg_id):
    tenant_id = get_tenant_or_send_error(tg_id)
    if not tenant_id:
        return

    locations = interAPI.tenant_apartments(tenant_id)

    locations_keyboard = InlineKeyboardMarkup()
    for loc in locations:
            button = InlineKeyboardButton(text=loc[1], callback_data=f"loc {loc[0]}")
            locations_keyboard.add(button)
        
    bot.send_message(tg_id, "ㅤㅤㅤКвартиры доступные вам:ㅤ", reply_markup=locations_keyboard)

def intercoms_menu(tg_id, apartment_id):
    intercoms = get_intercoms(tg_id, apartment_id)

    intercoms_keyboard = InlineKeyboardMarkup()
    for inter in intercoms:
            button = InlineKeyboardButton(text=inter[1], callback_data=f"{inter[0]}")
            intercoms_keyboard.add(button)
        
    bot.send_message(tg_id, "ㅤㅤㅤДомофоны подключенные к этой квартире:ㅤ", reply_markup=intercoms_keyboard)

def single_intercom_menu(tg_id, intercom_id):
    inter_id = intercom_id
    tenant_id = get_tenant_or_send_error(tg_id)
    if not tenant_id:
        return

    image = interAPI.intercom_image(inter_id, tenant_id)

    inter_actions_keyboard = InlineKeyboardMarkup(row_width=2)
    open_button = InlineKeyboardButton(text="Открыть", callback_data=f"open {inter_id}")
    refresh_button = InlineKeyboardButton(text="Обновить", callback_data=inter_id)

    inter_actions_keyboard.row(open_button, refresh_button)

    bot.send_photo(tg_id, image[0], reply_markup=inter_actions_keyboard)

# Базовый endpoint
@api_app.route('/tgbot/call', methods=['GET'])
def call_user():
    if "x-api-key" not in request.headers:
        return ({"message": "No token given"}), 403

    token = request.headers["x-api-key"]
    hashed_token = dbManager.get_hashed_api_key()

    if not bcrypt.checkpw(token, hashed_token):
        return ({"message": "Forbidden"}), 403

    # Извлекаем параметр "name" из URL
    print(request)
    inter_id = request.args["domofon_id"]
    tenant_id = request.args["tenant_id"]
    apartment_number = request.args["apartment_number"]

    tenant = dbManager.read_tenant_by_ten_id(tenant_id)
    if not tenant:
        return jsonify({"message": "No such tenant registered"}), 422

    tg_id = tenant[0]

    bot.send_message(tg_id, text=f"Вам звонят в {apartment_number} квартиру!")
    single_intercom_menu(tg_id, inter_id)
    return jsonify({"message": "Tenant has been called"}), 200

# Создание кнопки с запросом номера телефона
contact_button = KeyboardButton(text="Отправить номер", request_contact=True)

# Создание клавиатуры с кнопкой
reply_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
reply_keyboard.add(contact_button)

# Создание клавиатуры с функциями
actions_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
intercoms_button = KeyboardButton(text="Просмотреть квартиры")
actions_keyboard.add(intercoms_button)

def get_intercoms(tg_id, apartment_id):
    tenant_id = get_tenant_or_send_error(tg_id)
    if not tenant_id:
        return
    try:
        intercoms = interAPI.apartment_intercoms(apartment_id, tenant_id)
        return intercoms
    except ValidationError:
        return []

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Нажмите кнопку, чтобы отправить свой номер телефона", reply_markup=reply_keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    tenant = dbManager.read_tenant(call.message.chat.id)
    if not tenant:
        bot.send_message(call.message.chat.id, f"У вас нет домофонов...")
        return
    tenant_id = tenant[0]

    if call.data.isdigit():
        inter_id = int(call.data)
        single_intercom_menu(call.message.chat.id, inter_id)

    if call.data[:4] == "open":
        inter_id = int(call.data[5:])
        is_open = interAPI.open_intercom(inter_id, tenant_id)
        if is_open:
            bot.send_message(call.message.chat.id, f"Дверь успешно открыта")
        else:
            bot.send_message(call.message.chat.id, f"Ошибка, нельзя открыть дверь")
    
    if call.data[:3] == "loc":
        intercoms_menu(call.message.chat.id, int(call.data[4:]))

# Обработчик текстовых сообщений
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Просмотреть квартиры":
        apartments_menu(message.chat.id)

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    # Получаем номер телефона из сообщения
    user_phone_number = message.contact.phone_number[1:]

    try:
        tenant_id = interAPI.check_tenant(user_phone_number)
        apartments_menu(message.chat.id)
    except ValidationError:
        bot.send_message(message.chat.id, "Вы не зарегистрированы в нашей системе!")
        return

    dbManager.write_tenant(message.from_user.id, tenant_id, user_phone_number)
    bot.send_message(message.chat.id, f"Спасибо! Вы успешно вошли в систему!")
    bot.send_message(message.chat.id, text="Выберите действие", reply_markup=actions_keyboard)

# Запуск бота
api_thread = threading.Thread(target=api_app.run)
api_thread.start()
bot.polling(none_stop=True)

