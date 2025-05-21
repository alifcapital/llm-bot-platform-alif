import os
import telebot

import logging

from gpt_api_class import HR_RAG

# Инициализация токена Telegram-бота
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")


ALLOWED_USERNAMES = "https://t.me/Muborov_Alisher_720"



if not TELEGRAM_TOKEN:
    raise ValueError("Токен Telegram-бота не найден. Установите переменную окружения TELEGRAM_TOKEN.")

#  Создание экземпляра бота и RAG
bot = telebot.TeleBot(TELEGRAM_TOKEN)
gpt_rag = HR_RAG()

# 🛠 Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Постобработка ответа GPT для Telegram
import re
def format_violation_response(raw_text: str) -> str:
    lines = raw_text.splitlines()
    result = []

    for line in lines:
        # Удаляем жирные выделения **...**
        line = re.sub(r"\*\*(.*?)\*\*", r"\1", line)

        # Удаляем заголовки Markdown ###
        line = re.sub(r"^#+\s*", "", line).strip()

        if "Название документа:" in line:
            result.append("Название документа: " + line.split("Название документа:")[-1].strip())
        elif "Пункт или раздел:" in line:
            result.append("Пункт или раздел: " + line.split("Пункт или раздел:")[-1].strip())
        elif "Точный текст нарушенного положения:" in line:
            result.append("Точный текст положения: " + line.split("Точный текст нарушенного положения:")[-1].strip())
        elif "Объяснение:" in line:
            result.append("Объяснение: " + line.split("Объяснение:")[-1].strip())
        elif "Тип нарушения:" in line:
            result.append("Тип нарушения: " + line.split("Тип нарушения:")[-1].strip())
        elif "Оценка серьёзности нарушения:" in line:
            result.append("Серьёзность: " + line.split("Оценка серьёзности нарушения:")[-1].strip())
        elif "Итог" in line:
            result.append("\nИтог:")
        else:
            result.append(line.strip())

    return "\n".join(result)




# Проверка доступа по username
def check_auth(message):
    user = message.from_user
    user_id = user.id
    username = f"@{user.username}" if user.username else "без username"

    log_data = {
        'user_id': user_id,
        'username': username,
        'first_name': user.first_name,
        'last_name': user.last_name
    }

    if not user.username:
        bot.send_message(message.chat.id, "У вас не установлен username в Telegram!")
        logger.warning(f"Попытка несанкционированного доступа: {log_data}")
        return False

    if user.username not in ALLOWED_USERNAMES:
        logger.warning(f"Доступ запрещен для: {log_data}")
        bot.send_message(message.chat.id, "Доступ запрещен. Ваш username не в белом списке.")
        return False

    logger.info(f"Доступ разрешен: {log_data}")
    return True


#  Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not check_auth(message):
        return

    bot.reply_to(
        message,
        "Привет! Я HR бот. Опишите мне нарушение, и я постараюсь определить какие требования были нарушены."
    )


#  Обработка текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_query(message):
    if not check_auth(message):
        return

    user_query = message.text
    logger.info(f"Получен запрос: {user_query}")

    temp_message = bot.send_message(message.chat.id, "Ищу ответ...")

    try:
        answer = gpt_rag.ask(user_query)

        logger.info(f"Ответ на запрос: {answer}")

        formatted = format_violation_response(answer)

        bot.delete_message(chat_id=message.chat.id, message_id=temp_message.message_id)
        bot.send_message(message.chat.id, formatted)

    except Exception as e:
        logger.error(f"Ошибка при обработке запроса: {e}")
        bot.delete_message(chat_id=message.chat.id, message_id=temp_message.message_id)
        bot.send_message(message.chat.id, "Ошибка при поиске. Попробуйте снова позже.")

#  Запуск
if __name__ == "__main__":
    logger.info("Бот запущен!")
    bot.polling(none_stop=True)