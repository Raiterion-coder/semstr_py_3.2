import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from api import get_rating, get_summary
from kino_scraper import scrape_kinopoisk, scrape_upcoming_movies
from logger import log_interaction
from api import get_random_film

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = "👋 Привет! Я бот для получения информации о фильмах. Используй команды: /rating, /summary, /kinopoisk, /randomfilm"
    await update.message.reply_text(response)
    log_interaction(update, response)

# Команда для получения рейтинга фильма
async def rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    response = get_rating(query)
    await update.message.reply_text(response)
    log_interaction(update, response)

# Команда для получения описания фильма
async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    response = get_summary(query)
    await update.message.reply_text(response)
    log_interaction(update, response)
async def randomfilm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = get_random_film()
    await update.message.reply_text(response)
    log_interaction(update, response)
# Команда для поиска фильма на Кинопоиске
async def kinopoisk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    response = scrape_kinopoisk(query)
    await update.message.reply_text(response)
    log_interaction(update, response)

# Новая команда для получения ожидаемых фильмов
async def upcoming(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = scrape_upcoming_movies()  # Получаем список ожидаемых фильмов
    await update.message.reply_text(response)
    log_interaction(update, response)

# Инициализация бота
app = ApplicationBuilder().token(TOKEN).build()

# Добавляем обработчики команд
app.add_handler(CommandHandler("randomfilm", randomfilm))
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("rating", rating))
app.add_handler(CommandHandler("summary", summary))
app.add_handler(CommandHandler("kinopoisk", kinopoisk))
app.add_handler(CommandHandler("upcoming", upcoming))  # Добавляем новую команду для ожидаемых фильмов

# Запуск бота
app.run_polling()