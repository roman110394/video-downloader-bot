import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import yt_dlp

# Получаем токен из переменных окружения
BOT_TOKEN = os.environ.get("BOT_TOKEN")

YOUTUBE_REGEX = r'(https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+|https?://youtu\.be/[\w-]+)'

# Функция для скачивания и отправки видео
async def download_and_send(url: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        ydl_opts = {
            'format': 'best[filesize<50M]',
            'outtmpl': '/tmp/video.%(ext)s',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await update.message.reply_video(video=open(filename, 'rb'))
        os.remove(filename)

    except Exception as e:
        await update.message.reply_text(f"Ошибка при загрузке: {e}")

# Функция для обработки сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    match = re.search(YOUTUBE_REGEX, text)
    if match:
        await download_and_send(match.group(0), update, context)

# Создаём приложение и подключаем обработчик
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Запускаем бота без использования порта, так как он не требуется
if __name__ == "__main__":
    app.run_polling()
