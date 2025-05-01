import random
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Кнопки
main_knop = ReplyKeyboardMarkup([["/dice", "/timer"]], resize_keyboard=True)

dice_knop = ReplyKeyboardMarkup([
    ["1 кубик с 6-ю гранями", "2 кубика с 6-ю гранями"],
    ["кубик с 20 гранями"],
    ["Назад"]
], resize_keyboard=True)

timer_knop = ReplyKeyboardMarkup([
    ["30 секунд", "1 минута"],
    ["5 минут"],
    ["Назад"]
], resize_keyboard=True)

close_knop = ReplyKeyboardMarkup([["/close"]], resize_keyboard=True)

timers = {}


# Команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот. Выбери действие:", reply_markup=main_knop)


async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выбери кубик:", reply_markup=dice_knop)


async def timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выбери таймер:", reply_markup=timer_knop)


async def close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    task = timers.pop(user_id, None)
    if task:
        task.cancel()
        await update.message.reply_text("Таймер сброшен.", reply_markup=main_knop)
    else:
        await update.message.reply_text("Нет активного таймера.", reply_markup=main_knop)


# Таймеры
async def handle_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    mapping = {
        "30 секунд": 30,
        "1 минута": 60,
        "5 минут": 300
    }

    seconds = mapping.get(text)
    if not seconds:
        return

    if user_id in timers:
        timers[user_id].cancel()

    await update.message.reply_text(f"Засек {text}", reply_markup=close_knop)

    async def timer_task():
        try:
            await asyncio.sleep(seconds)
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f"{text} истекло!", reply_markup=main_knop)
            timers.pop(user_id, None)
        except asyncio.CancelledError:
            pass

    task = asyncio.create_task(timer_task())
    timers[user_id] = task


# Обработка кубиков
async def handle_dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "1 кубик с 6-ю гранями":
        await update.message.reply_text(f"Выпало: {random.randint(1, 6)}", reply_markup=dice_knop)
    elif text == "2 кубика с 6-ю гранями":
        await update.message.reply_text(
            f"Выпало: {random.randint(1, 6)} и {random.randint(1, 6)}",
            reply_markup=dice_knop
        )
    elif text == "кубик с 20 гранями":
        await update.message.reply_text(f"Выпало: {random.randint(1, 20)}", reply_markup=dice_knop)


async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выбери действие:", reply_markup=main_knop)


async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пожалуйста, используйте кнопки или команды.")


def main():
    app = ApplicationBuilder().token("токен сюда").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dice", dice))
    app.add_handler(CommandHandler("timer", timer))
    app.add_handler(CommandHandler("close", close))

    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^30 секунд|1 минута|5 минут$"), handle_timer))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^1 кубик с 6|2 кубика с 6|кубик с 20"), handle_dice))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Назад$"), go_back))

    app.add_handler(MessageHandler(filters.TEXT, fallback))

    app.run_polling()


if __name__ == "__main__":
    main()
