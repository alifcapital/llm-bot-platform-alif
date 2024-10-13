# Репозиторий для перевода сложных и больших Word вайлов

# Поддерживаемые форматы:

- docx

# Локальный запуск

`docker build -t gpt .` - сборка контейнера

`docker run -it --rm -p 8000:8000 -v %cd%:/app -e OPENAI_API_KEY=YOUR_KEY gpt`