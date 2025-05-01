from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Описание залов
hall_descriptions = {
    "Вход": "Добро пожаловать! Пожалуйста, сдайте верхнюю одежду в гардероб!",
    "Зал 1": "В данном зале представлено искусство созданное в Кемерово.",
    "Зал 2": "В данном зале представлены экспонаты лучшего угля мира.",
    "Зал 3": "В данном зале собраны макеты белазов.",
    "Зал 4": "В данном зале есть кафешка с вкусной едой.",
    "Выход": "Всего доброго, не забудьте забрать верхнюю одежду в гардеробе!"
}

# Возможные переходы между залами
transitions = {
    "Вход": {"Зал 1": "Перейти в Зал 1"},
    "Зал 1": {
        "Зал 2": "Перейти в Зал 2",
        "Выход": "Выйти из музея"
    },
    "Зал 2": {"Зал 3": "Перейти в Зал 3"},
    "Зал 3": {
        "Зал 1": "Вернуться в Зал 1",
        "Зал 4": "Перейти в Зал 4"
    },
    "Зал 4": {"Зал 1": "Вернуться в Зал 1"},
    "Выход": {"Вход": "Войти в музей снова"}  # Добавлена возможность повторного входа
}

user_states = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_states[user_id] = "Вход"
    await send_hall_info(update, context, user_id)


async def send_hall_info(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    current_hall = user_states[user_id]
    description = hall_descriptions[current_hall]

    keyboard = [
        [button_text]
        for button_text in transitions[current_hall].values()
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(description, reply_markup=reply_markup)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    current_hall = user_states.get(user_id, "Вход")
    message_text = update.message.text

    # Поиск соответствующего перехода
    for hall, button_text in transitions[current_hall].items():
        if message_text == button_text:
            user_states[user_id] = hall
            await send_hall_info(update, context, user_id)
            return

    await update.message.reply_text("Используйте кнопки для навигации.")


def main() -> None:
    application = Application.builder().token("токен сюда").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()


if __name__ == '__main__':
    main()
