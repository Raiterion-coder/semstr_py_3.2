from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет я бот! Используй команды:\n"
        "/time - текущее время\n"
        "/date - текущая дата"
    )


async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_time = datetime.now().strftime("%H:%M:%S")
    await update.message.reply_text(f"Текущее время: {current_time}")


async def date_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_date = datetime.now().strftime("%d.%m.%Y")
    await update.message.reply_text(f"Сегодняшняя дата: {current_date}")


def main():
    application = Application.builder().token("сюда токен").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("time", time_command))
    application.add_handler(CommandHandler("date", date_command))

    application.run_polling()


if __name__ == '__main__':
    main()
