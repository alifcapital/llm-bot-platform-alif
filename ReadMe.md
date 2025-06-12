# LLM Bot Platform Alif

Это приложение представляет собой платформу для работы с большими языковыми моделями (LLM) и обработки документов.

## Требования
- Python 3.8 или выше
- Docker и Docker Compose
- PostgreSQL 13 или выше

## Установка и запуск

### Вариант 1: Локальный запуск (без Docker)

1. Клонируйте репозиторий:
```bash
git clone [URL репозитория]
cd llm-bot-platform-alif
```

2. Создайте виртуальное окружение Python:
```bash
python -m venv venv
```

3. Активируйте виртуальное окружение:
- Для Windows:
```bash
venv\Scripts\activate
```
- Для Linux/Mac:
```bash
source venv/bin/activate
```

4. Установите зависимости:
```bash
pip install -r requirements.txt
```

5. Создайте файл `.env` в корневой директории проекта со следующими параметрами:
```
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_database_name
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=postgresql://username:password@localhost:5432/dbname
# Добавьте другие необходимые переменные окружения
```

6. Запустите PostgreSQL базу данных:
```bash
docker run -d --name postgres_db --network app-network --env-file=.env -v postgres_data:/var/lib/postgresql/data -p 5432:5432 postgres:13-alpine
```

7. Запустите приложение:
```bash
python main.py
```

### Вариант 2: Запуск с использованием Docker

1. Клонируйте репозиторий:
```bash
git clone [URL репозитория]
cd llm-bot-platform-alif
```

2. Создайте файл `.env` в корневой директории проекта (как описано выше)

3. Соберите Docker образ:
```bash
docker build -t gpt .
```

4. Запустите приложение в Docker:
```bash
docker run -it --rm -p 5000:5000 -v %cd%:/app --env-file .env llm-bot-platform-alif bash
```

### Вариант 3: Запуск с использованием Docker Compose (рекомендуемый способ)

1. Клонируйте репозиторий:
```bash
git clone [URL репозитория]
cd llm-bot-platform-alif
```

2. Создайте файл `.env` в корневой директории проекта со следующими параметрами:
```
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_database_name
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=postgresql://username:password@localhost:5432/dbname
# Добавьте другие необходимые переменные окружения
```

3. Соберите Docker образ:
```bash
docker build -t llm-bot-platform-alif .
```

4. Запустите приложение с помощью Docker Compose:
```bash
docker-compose up -d
```

5. Проверьте, что все контейнеры запущены:
```bash
docker-compose ps
```

6. Для просмотра логов приложения:
```bash
docker-compose logs -f bot
```

7. Для остановки приложения:
```bash
docker-compose down
```

8. Для остановки приложения и удаления всех данных (включая базу данных):
```bash
docker-compose down -v
```

Примечания по Docker Compose:
- Приложение будет доступно по адресу: http://localhost:5000
- База данных PostgreSQL будет доступна на порту 5432
- Все данные базы данных сохраняются в Docker volume `postgres_data`
- При перезапуске контейнеров данные сохраняются
- Для применения изменений в коде после редактирования файлов, перезапустите контейнеры:
```bash
docker-compose down
docker-compose up -d
```

## Структура проекта
- `main.py` - основной файл приложения
- `forms.py` - формы для веб-интерфейса
- `models.py` - модели данных
- `RAG/` - директория с компонентами RAG (Retrieval-Augmented Generation)
- `src/` - исходный код приложения
- `templates/` - HTML шаблоны
- `requirements.txt` - зависимости Python
- `Dockerfile` - конфигурация Docker
- `docker-compose.yml` - конфигурация Docker Compose

## Устранение неполадок

1. Если возникают проблемы с подключением к базе данных:
   - Проверьте, что PostgreSQL запущен
   - Убедитесь, что параметры подключения в `.env` файле корректны
   - Проверьте, что порт 5432 не занят другим приложением

2. Если возникают проблемы с Docker:
   - Убедитесь, что Docker запущен
   - Проверьте права доступа к Docker
   - Очистите кэш Docker: `docker system prune -a`

## Поддержка

При возникновении проблем создайте issue в репозитории проекта или обратитесь к команде разработки.