import logging
import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, ConversationHandler, filters
)

from api import get_rating, get_summary, get_random_quote, get_random_film
from kino_scraper import scrape_kinopoisk, get_top_films
from logger import log_interaction

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

# Состояния для ConversationHandler
RATING, SUMMARY, KINOPOISK = range(3)
TOPFILMS = 4  # после RATING, SUMMARY, KINOPOISK

# Кнопки для команд
buttons = [
    ["/rating", "/summary"],
    ["/kinopoisk", "/randomfilm"],
    ["/quote", "/topfilms"]
]
reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = (
        "🎬 *Привет! Я бот для киноманов!*\n\n"
        "Выбери одну из команд ниже или введи её:\n\n"
        "⭐ /rating — получить рейтинг фильма \n"
        "📝 /summary — получить краткое описание фильма\n"
        "🔍 /kinopoisk — поиск фильма на Кинопоиске\n"
        "🎲 /randomfilm — случайный фильм с описанием и рейтингами\n"
        "📅 /topfilms — топ-5 фильмов по году с сайта Film.ru\n"
        "💬 /quote — случайная цитата из фильма\n\n"
        "Просто нажми на кнопку или введи команду, а я помогу!"
    )
    await update.message.reply_text(response, reply_markup=reply_markup)
    log_interaction(update, response)


# -- Рейтинг --
async def rating_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введите название фильма для рейтинга на английском языке:", reply_markup=ReplyKeyboardRemove()
    )
    return RATING


async def handle_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    title = update.message.text
    response = get_rating(title) or f"Фильм не найден: {title}"
    await update.message.reply_text(response, reply_markup=reply_markup)
    log_interaction(update, response)
    return ConversationHandler.END


# -- Описание --
async def summary_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введите название фильма для описания на английском языке:", reply_markup=ReplyKeyboardRemove()
    )
    return SUMMARY


async def handle_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    title = update.message.text
    response = get_summary(title) or f"Фильм не найден: {title}"
    await update.message.reply_text(response, reply_markup=reply_markup)
    log_interaction(update, response)
    return ConversationHandler.END


# -- Кинопоиск --
async def kinopoisk_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введите название фильма для поиска на Кинопоиске:", reply_markup=ReplyKeyboardRemove()
    )
    return KINOPOISK


# Импортируем скрапер

async def topfilms_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введите год (например, 2021):", reply_markup=ReplyKeyboardRemove()
    )
    return TOPFILMS


async def handle_topfilms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        year = int(update.message.text.strip())
        response = get_top_films(year)
    except ValueError:
        response = "❌ Пожалуйста, введите корректный год (например, 2021)."

    await update.message.reply_text(response, reply_markup=reply_markup, parse_mode="Markdown")
    log_interaction(update, response)
    return ConversationHandler.END


async def handle_kinopoisk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    title = update.message.text
    response = scrape_kinopoisk(title)
    await update.message.reply_text(response, reply_markup=reply_markup)
    log_interaction(update, response)
    return ConversationHandler.END


# -- Случайный фильм --
async def randomfilm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = get_random_film()
    await update.message.reply_text(response, reply_markup=reply_markup)
    log_interaction(update, response)


# -- Цитата --
async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = get_random_quote()
    await update.message.reply_text(response, reply_markup=reply_markup)
    log_interaction(update, response)


# -- Ожидаемые фильмы --


# Создаем приложение и добавляем обработчики
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("quote", quote))
app.add_handler(CommandHandler("randomfilm", randomfilm))

# ConversationHandler для /rating
app.add_handler(
    ConversationHandler(
        entry_points=[CommandHandler("rating", rating_command)],
        states={RATING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_rating)]},
        fallbacks=[],
    )
)
app.add_handler(
    ConversationHandler(
        entry_points=[CommandHandler("topfilms", topfilms_command)],
        states={TOPFILMS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_topfilms)]},
        fallbacks=[],
    )
)

# ConversationHandler для /summary
app.add_handler(
    ConversationHandler(
        entry_points=[CommandHandler("summary", summary_command)],
        states={SUMMARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_summary)]},
        fallbacks=[],
    )
)

# ConversationHandler для /kinopoisk
app.add_handler(
    ConversationHandler(
        entry_points=[CommandHandler("kinopoisk", kinopoisk_command)],
        states={KINOPOISK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_kinopoisk)]},
        fallbacks=[],
    )
)

# Запуск бота
app.run_polling()
