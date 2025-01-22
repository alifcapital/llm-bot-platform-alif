import os
import telebot
import logging

from gpt_api_class import GPT_API, RAG

# Инициализация токена Telegram-бота
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise ValueError("Токен Telegram-бота не найден. Установите переменную окружения TELEGRAM_TOKEN.")

# Создание экземпляра бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)
gpt_rag = RAG()

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        "Привет! Я бот RAG. Задайте мне любой вопрос, и я постараюсь дать ответ."
    )

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_query(message):
    user_query = message.text
    logger.info(f"Получен запрос: {user_query}")

    # Отправка временного сообщения
    temp_message = bot.send_message(message.chat.id, "Ищу ответ...")

    try:
        # Вызов метода RAG
        answer = gpt_rag.execute_query(user_query)
        logger.info(f"Ответ на запрос: {answer}")

        # Удаление временного сообщения
        bot.delete_message(chat_id=message.chat.id, message_id=temp_message.message_id)

        # Отправка ответа пользователю
        bot.send_message(message.chat.id, answer)

    except Exception as e:
        # Логирование ошибки
        logger.error(f"Ошибка при обработке запроса: {e}")

        # Удаление временного сообщения
        bot.delete_message(chat_id=message.chat.id, message_id=temp_message.message_id)

        # Отправка сообщения об ошибке
        bot.send_message(message.chat.id, "Произошла ошибка при поиске ответа. Пожалуйста, попробуйте снова.")

# Запуск бота
if __name__ == "__main__":
    logger.info("Бот запущен!")
    bot.polling(none_stop=True)
