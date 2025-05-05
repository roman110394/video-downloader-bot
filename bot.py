import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import yt_dlp
import logging
from flask import Flask, request

app = Flask(__name__)

# Токен бота, полученный от BotFather
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Регулярное выражение для поиска ссылок на YouTube
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

# Flask route для webhook
@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data(as_text=True)
    update = Update.de_json(json_str, app.bot)
    app.update_queue.put(update)
    return 'OK', 200

# Настройка webhook
async def set_webhook():
    url = f"https://video-downloader-bot-zh4x.onrender.com/{BOT_TOKEN}"  # Используем свой URL
    await app.bot.set_webhook(url)

if __name__ == "__main__":
    app.run(debug=True)
