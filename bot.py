from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os
import asyncio

TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()

app = Flask(__name__)

# Обработчики команд и сообщений
async def start(update: Update, context):
    await update.message.reply_text("Привет!")

async def handle_message(update: Update, context):
    await update.message.reply_text("Сообщение принято.")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Обработка POST-запросов Telegram (вебхук)
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(force=True)
    print("Got update:", data)
    update = Update.de_json(data, bot)
    asyncio.get_event_loop().create_task(application.process_update(update))
    return 'ok'

# Установка вебхука
def set_webhook():
    url = "https://video-downloader-bot-zh4x.onrender.com/webhook"
    result = asyncio.run(bot.set_webhook(url))
    print("Webhook set:", result)

# Запуск Flask-приложения и установка вебхука
if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=10000)
