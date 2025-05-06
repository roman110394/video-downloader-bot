from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
import os
import asyncio
import logging
from telegram.error import InvalidToken, TelegramError

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Инициализация Flask и Telegram
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    logger.error("BOT_TOKEN is not set in environment variables")
    raise ValueError("BOT_TOKEN is not set")

try:
    bot = Bot(token=TOKEN)
except InvalidToken as e:
    logger.error(f"Invalid BOT_TOKEN: {e}")
    raise

app = Flask(__name__)

# Создание и инициализация Application
application = Application.builder().token(TOKEN).build()

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug(f"Received /start command from user: {update.effective_user.id}")
    await update.message.reply_text("Привет")

# Регистрация обработчиков
application.add_handler(CommandHandler("start", start))

# Обработка вебхука
@app.route('/webhook', methods=['POST'])
async def webhook():
    try:
        data = request.get_json(force=True)
        if not data:
            logger.error("No JSON data received")
            return 'ok', 400
        
        logger.debug(f"Received update: {data}")
        update = Update.de_json(data, bot)
        if not update:
            logger.error("Failed to parse update")
            return 'ok', 400
        
        await application.process_update(update)
        return 'ok'
    except Exception as e:
        logger.error(f"Error in webhook: {e}", exc_info=True)
        return 'ok', 500

# Установка вебхука и инициализация приложения
async def initialize_and_set_webhook():
    try:
        await application.initialize()
        logger.info("Application initialized")
        webhook_url = "https://video-downloader-bot-zh4x.onrender.com/webhook"
        success = await bot.set_webhook(webhook_url)
        logger.info(f"Webhook set: {success}")
    except TelegramError as e:
        logger.error(f"Failed to set webhook: {e}")
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")

# Запуск приложения
if __name__ == "__main__":
    logger.info("Starting application")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(initialize_and_set_webhook())
    port = int(os.environ.get("PORT", 8443))
    app.run(host="0.0.0.0", port=port)