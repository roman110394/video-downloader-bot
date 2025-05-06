from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
import yt_dlp
import ffmpeg
import re
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

application = Application.builder().token(TOKEN).build()

app = Flask(__name__)

# Функция для проверки, является ли ссылка YouTube
def is_youtube_url(url):
    youtube_regex = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$'
    return re.match(youtube_regex, url)

# Функция для скачивания и сжатия видео
async def download_and_compress_video(url, output_file="sized_video.mp4"):
    try:
        logger.debug(f"Starting download for URL: {url}")
        # Параметры для yt-dlp
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': 'downloaded_video.%(ext)s',
            'quiet': True,
        }

        # Скачивание видео
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Поиск скачанного файла
        for file in os.listdir():
            if file.startswith("downloaded_video"):
                input_file = file
                break
        else:
            raise Exception("Downloaded file not found")

        logger.debug(f"Compressing video: {input_file} to {output_file}")
        # Сжатие видео с помощью ffmpeg
        stream = ffmpeg.input(input_file)
        stream = ffmpeg.output(
            stream,
            output_file,
            vcodec='libx264',
            acodec='aac',
            video_bitrate='500k',
            audio_bitrate='128k',
            s='854x480',
            preset='fast',
            **{'movflags': '+faststart'}
        )
        ffmpeg.run(stream, overwrite_output=True)

        # Удаление исходного файла
        os.remove(input_file)
        logger.debug(f"Compression successful, output: {output_file}")
        return output_file
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        return None

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug(f"Received /start command from user: {update.effective_user.id}")
    await update.message.reply_text("Привет! Отправь мне ссылку на YouTube-видео, и я скачаю и отправлю его тебе.")

# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    logger.debug(f"Received message: {url}")
    if not is_youtube_url(url):
        await update.message.reply_text("Пожалуйста, отправь корректную ссылку на YouTube-видео.")
        return

    await update.message.reply_text("Скачиваю и обрабатываю видео, подожди немного...")
    
    output_file = "sized_video.mp4"
    result = await download_and_compress_video(url, output_file)
    
    if result and os.path.exists(output_file):
        file_size = os.path.getsize(output_file) / (1024 * 1024)  # Размер в МБ
        logger.debug(f"Video size: {file_size} MB")
        if file_size > 50:
            await update.message.reply_text("Сжатое видео слишком большое (>50 МБ). Попробуй другое видео.")
            os.remove(output_file)
            return
        
        with open(output_file, 'rb') as video:
            await update.message.reply_video(video=video, supports_streaming=True)
        os.remove(output_file)
        logger.debug("Video sent successfully")
    else:
        await update.message.reply_text("Ошибка при скачивании или обработке видео. Попробуй другую ссылку.")

# Регистрация обработчиков
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

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

# Установка вебхука
async def set_webhook():
    webhook_url = "https://video-downloader-bot-zh4x.onrender.com/webhook"
    try:
        success = await bot.set_webhook(webhook_url)
        logger.info(f"Webhook set: {success}")
    except TelegramError as e:
        logger.error(f"Failed to set webhook: {e}")

# Запуск приложения
if __name__ == "__main__":
    logger.info("Starting application")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(set_webhook())
    port = int(os.environ.get("PORT", 8443))
    app.run(host="0.0.0.0", port=port)