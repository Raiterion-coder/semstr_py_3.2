import json
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TESTING, ANSWERING = range(2)


class QuizBot:
    def __init__(self):
        self.questions = []
        self.current_question = 0
        self.correct_answers = 0
        self.user_answers = []
        self.test_questions = []

    def load_questions(self, filename):
        # Загрузка вопросов из JSON-файла
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            self.questions = data["test"]

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # 10 случайных вопросов
        self.test_questions = random.sample(self.questions, 10)
        self.current_question = 0
        self.correct_answers = 0
        self.user_answers = []

        await update.message.reply_text(
            "Привет я бот! Давай проверим твои знания про нашу Кемеровскую область. "
            "Я задам тебе 10 вопросов.\n\n"
            f"Первый вопрос: {self.test_questions[self.current_question]['question']}\n\n"
            "Можешь прервать тест в любой момент командой /stop"
        )

        return ANSWERING

    async def handle_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_answer = update.message.text.strip()
        correct_answer = self.test_questions[self.current_question]["response"]

        self.user_answers.append({
            "question": self.test_questions[self.current_question]["question"],
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": user_answer.lower() == correct_answer.lower()
        })

        if self.user_answers[-1]["is_correct"]:
            self.correct_answers += 1

        self.current_question += 1

        if self.current_question < len(self.test_questions):
            await update.message.reply_text(
                f"Следующий вопрос: {self.test_questions[self.current_question]['question']}"
            )
            return ANSWERING
        else:
            # Тест завершен
            await update.message.reply_text(
                f"Тест завершен! Правильных ответов: {self.correct_answers}/10\n\n"
                "Хочешь попробовать еще раз? Нажми /start\n"
                "Если не хочешь, заверши работу командой /stop"
            )
            return ConversationHandler.END

    async def stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if self.current_question > 0:
            await update.message.reply_text(
                f"Тест прерван. Правильных ответов: {self.correct_answers}/{self.current_question}\n\n"
                "Хочешь попробовать еще раз? Нажми /start"
            )
        else:
            await update.message.reply_text(
                "Тест не был начат. Нажми /start"
            )

        return ConversationHandler.END


def main():
    # Создаем экземпляр бота
    quiz_bot = QuizBot()

    try:
        # Загружаем вопросы из файла
        quiz_bot.load_questions("vopros.json")
    except FileNotFoundError:
        print("Ошибка: файл vopros.json не найден")
        return
    except json.JSONDecodeError:
        print("Ошибка: файл questions.json имеет неверный формат")
        return
    except ValueError as e:
        print(f"Ошибка: {e}")
        return

    # Создаем Application и передаем токен
    application = Application.builder().token("токен сюда").build()

    # Создаем ConversationHandler для управления диалогом
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', quiz_bot.start)],
        states={
            ANSWERING: [MessageHandler(filters.TEXT & ~filters.COMMAND, quiz_bot.handle_answer)]
        },
        fallbacks=[CommandHandler('stop', quiz_bot.stop)],
    )

    # Добавляем обработчик в приложение
    application.add_handler(conv_handler)

    # Запускаем бота
    print("Бот запущен...")
    application.run_polling()


if __name__ == '__main__':
    main()
