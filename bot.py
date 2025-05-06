from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os
import asyncio

# Инициализация Flask и Telegram
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

# Обработка вебхука
@app.route('/webhook', methods=['POST'])
async def webhook():
    data = request.get_json(force=True)
    print("Got update:", data)
    update = Update.de_json(data, bot)
    await application.process_update(update)  # Асинхронная обработка обновления
    return 'ok'

# Установка вебхука
async def set_webhook():
    url = "https://video-downloader-bot-zh4x.onrender.com/webhook"
    success = await bot.set_webhook(url)
    print("Webhook set:", success)

# Запуск приложения
if __name__ == "__main__":
    # Установка вебхука при запуске
    loop = asyncio.get_event_loop()
    loop.run_until_complete(set_webhook())
    
    # Запуск Flask через gunicorn не требуется здесь, так как Render сам управляет этим
    # Для локального тестирования можно оставить app.run
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)