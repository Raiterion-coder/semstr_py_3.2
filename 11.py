import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext
import requests

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Клавиатура для выбора языка
LANGUAGE_KEYBOARD = ReplyKeyboardMarkup(
    [['🇷🇺 Русский -> 🇬🇧 Английский', '🇬🇧 Английский -> 🇷🇺 Русский']],
    resize_keyboard=True,
    one_time_keyboard=False
)


# Функция для перевода текста с помощью MyMemory API
async def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    try:
        url = f"https://api.mymemory.translated.net/get?q={text}&langpair={source_lang}|{target_lang}"
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200 and data['responseStatus'] == 200:
            return data['responseData']['translatedText']
        else:
            logger.error(f"Translation error: {data.get('responseDetails', 'Unknown error')}")
            return "Произошла ошибка при переводе."
    except Exception as e:
        logger.error(f"API request failed: {e}")
        return "Не удалось подключиться к сервису перевода."


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! Я бот-переводчик. Выбери направление перевода и отправь мне любой текст.",
        reply_markup=LANGUAGE_KEYBOARD
    )


# Обработчик текстовых сообщений
async def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    text = update.message.text

    if text in ['🇷🇺 Русский -> 🇬🇧 Английский', '🇬🇧 Английский -> 🇷🇺 Русский']:
        context.user_data['translation_direction'] = text
        direction = "Русский -> Английский" if text.startswith('🇷🇺') else "Английский -> Русский"
        await update.message.reply_text(
            f"Выбрано направление перевода: {direction}. Отправьте текст.",
            reply_markup=LANGUAGE_KEYBOARD
        )
    else:
        if 'translation_direction' not in context.user_data:
            await update.message.reply_text(
                "Сначала выберите направление перевода.",
                reply_markup=LANGUAGE_KEYBOARD
            )
            return

        if context.user_data['translation_direction'] == '🇷🇺 Русский -> 🇬🇧 Английский':
            source_lang, target_lang = 'ru', 'en'
        else:
            source_lang, target_lang = 'en', 'ru'

        # Выполнение перевода
        translated_text = await translate_text(text, source_lang, target_lang)
        await update.message.reply_text(translated_text, reply_markup=LANGUAGE_KEYBOARD)


def main() -> None:
    application = Application.builder().token("токен сюда").build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()


if __name__ == '__main__':
    main()
