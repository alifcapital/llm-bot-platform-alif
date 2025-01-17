# Репозиторий для перевода сложных и больших Word вайлов

# Поддерживаемые форматы:

- docx

# Локальный запуск

`docker build -t gpt .` - сборка контейнера

`docker run -it --rm -p 8001:8001 -v %cd%:/app -e OPENAI_API_KEY=YOUR_KEY gpt`

docker run -it --rm -p 8001:8001 -v C:\Users\zheny\Documents\gpt-translator-service:/app -e OPENAI_API_KEY=YOUR_KEY gpt bash

# Выгрузка статей с javob.alif.tj

curl --location 'https://apijavob.alif.tj/api/articles' \
--header 'Authorization: Bearer TOKEN