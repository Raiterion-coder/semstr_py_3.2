import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from io import BytesIO

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

YANDEX_GEOCODE_API_KEY = ''
YANDEX_MAP_API_KEY = ''
GEOCODE_URL = 'https://geocode-maps.yandex.ru/1.x/'
MAP_URL = 'https://static-maps.yandex.ru/1.x/'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет я бот! Отправь мне название места или адрес, и я пришлю тебе карту с этим местом и отметкой.\n"
        "Например: 'Кемерово,Площадь Пушкина' или 'Москва, Красная площадь'"
    )


async def geocode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_query = update.message.text

    try:
        geocode_params = {
            'apikey': YANDEX_GEOCODE_API_KEY,
            'geocode': user_query,
            'format': 'json'
        }

        headers = {'User-Agent': 'TelegramBot/1.0'}

        geocode_response = requests.get(GEOCODE_URL, params=geocode_params, headers=headers)
        geocode_response.raise_for_status()
        geocode_data = geocode_response.json()

        found_results = int(
            geocode_data['response']['GeoObjectCollection']['metaDataProperty']['GeocoderResponseMetaData']['found'])

        if found_results == 0:
            await update.message.reply_text("К сожалению, ничего не найдено. Попробуйте уточнить запрос.")
            return

        first_result = geocode_data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
        pos = first_result['Point']['pos']
        lon, lat = pos.split()
        address = first_result['metaDataProperty']['GeocoderMetaData']['text']

        map_params = {
            'l': 'map',
            'pt': f'{lon},{lat},pm2rdl',  # pm2rdl = red marker
            'll': f'{lon},{lat}',
            'z': '14',
            'size': '650,450',
            'apikey': YANDEX_MAP_API_KEY
        }

        map_response = requests.get(MAP_URL, params=map_params, headers=headers)
        map_response.raise_for_status()

        with BytesIO(map_response.content) as map_image:
            await update.message.reply_photo(
                photo=map_image,
                caption=f"{address}\nКоординаты: {lat}, {lon}",
                parse_mode='Markdown'
            )

    except requests.exceptions.HTTPError as http_err:
        logger.error(
            f"HTTP error: {http_err} - Response: {http_err.response.text if http_err.response else 'No response'}")
        await update.message.reply_text("Произошла ошибка при обращении к сервису карт.")
    except Exception as err:
        logger.error(f"Unexpected error: {err}", exc_info=True)
        await update.message.reply_text("Произошла непредвиденная ошибка.")


def main():
    application = Application.builder().token("токен для телеграм бота сюда").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, geocode))

    application.run_polling()


if __name__ == '__main__':
    main()
