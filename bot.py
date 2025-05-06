from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters

TOKEN = "YOUR_BOT_TOKEN"
bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()

app = Flask(__name__)

# Обработчики
async def start(update: Update, context):
    await update.message.reply_text("Привет! Я бот.")

async def handle_message(update: Update, context):
    await update.message.reply_text("Я получил ваше сообщение.")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# СИНХРОННЫЙ webhook, чтобы Flask не ругался
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return 'ok'

# СИНХРОННАЯ установка вебхука
def set_webhook():
    url = "https://video-downloader-bot-zh4x.onrender.com/webhook"
    import asyncio
    asyncio.run(bot.set_webhook(url))

# Запуск
if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=10000)
