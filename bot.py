from flask import Flask, request
import logging
import asyncio

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
async def webhook():
    try:
        data = request.get_json(force=True)
        logger.debug(f"Received update: {data}")
        return 'ok'
    except Exception as e:
        logger.error(f"Error in webhook: {e}", exc_info=True)
        return 'ok', 500

if __name__ == "__main__":
    logger.info("Starting minimal application")
    port = int(os.environ.get("PORT", 8443))
    app.run(host="0.0.0.0", port=port)