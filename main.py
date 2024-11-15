import telebot

bot = telebot.TeleBot('7802215334:AAHXnUEFTCrHQiniazQbrRZYECxYOHj6Ykc')

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    bot.send_message(message.from_user.id, message.text)

bot.polling()