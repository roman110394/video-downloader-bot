import os
import json
from flask import Flask, request, jsonify
from telegram import Bot
from telegram.ext import Dispatcher, Update
from telegram.ext import CommandHandler, MessageHandler, filters

# Инициализация приложения Flask
app = Flask(__name__)

# Токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN')  # Убедитесь, что ваш токен хранится в переменной окружения
bot = Bot(token=BOT_TOKEN)

# Инициализация диспетчера для обработки обновлений
dispatcher = Dispatcher(bot, None, workers=0)

# Установите правильный маршрут для обработки вебхука
@app.route('/webhook', methods=['POST'])
def webhook():
    # Получаем обновление от Telegram
    json_str = request.get_data().decode('UTF-8')
    update = Update.de_json(json.loads(json_str), bot)
    
    # Диспетчер обрабатывает обновление
    dispatcher.process_update(update)
    
    return jsonify({"status": "ok"})


# Обработчик команды /start
def start(update, context):
    update.message.reply_text("Привет, я бот для скачивания видео с YouTube!")

# Обработчик текстовых сообщений
def handle_message(update, context):
    update.message.reply_text("Ты прислал сообщение!")

# Регистрируем обработчики команд
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Функция для установки вебхука в Telegram
def set_webhook():
    webhook_url = 'https://video-downloader-bot-zh4x.onrender.com/webhook'
    bot.set_webhook(url=webhook_url)
    print("Webhook установлен.")

if __name__ == '__main__':
    set_webhook()  # Устанавливаем вебхук перед запуском
    app.run(host='0.0.0.0', port=10000)
