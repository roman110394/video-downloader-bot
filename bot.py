import os
import re
import telegram
from flask import Flask, request
import yt_dlp

app = Flask(__name__)

# Инициализация бота с токеном из переменной окружения
bot = telegram.Bot(token=os.environ.get("TELEGRAM_TOKEN"))

# Регулярное выражение для поиска ссылок на YouTube
YOUTUBE_REGEX = r'(https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+|https?://youtu\.be/[\w-]+)'

# Основной маршрут для GET запросов
@app.route('/')
def home():
    return "Video Downloader Bot is up and running!"

# Обработка входящих обновлений через вебхук
@app.route('/webhook', methods=['POST'])
def webhook():
    # Получаем данные из запроса
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    # Извлекаем информацию из сообщения
    text = update.message.text or ""
    chat_id = update.message.chat_id

    # Если в сообщении есть ссылка на YouTube
    match = re.search(YOUTUBE_REGEX, text)
    if match:
        url = match.group(0)
        download_and_send(url, chat_id)
    
    return 'OK'

async def download_and_send(url: str, chat_id: int):
    try:
        ydl_opts = {
            'format': 'best[filesize<50M]',
            'outtmpl': '/tmp/video.%(ext)s',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # Отправляем видео в чат
        with open(filename, 'rb') as video_file:
            bot.send_video(chat_id=chat_id, video=video_file)

        # Удаляем временный файл
        os.remove(filename)

    except Exception as e:
        bot.send_message(chat_id=chat_id, text=f"Ошибка при загрузке: {e}")

if __name__ == '__main__':
    # Запуск Flask-сервера, слушая на всех интерфейсах и порту, указанном в переменной окружения PORT
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
