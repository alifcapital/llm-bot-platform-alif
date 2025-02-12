# Репозиторий для перевода сложных и больших Word вайлов

# Поддерживаемые форматы:

- docx

# Локальный запуск

`docker build -t gpt .` - сборка контейнера

`docker build -f Dockerfile_bot -t gpt-bot .` - сборка контейнера

`docker run -it --rm -p 8000:8000 -v %cd%:/app --env-file .env gpt bash`

# Выгрузка статей с javob.alif.tj

curl --location 'https://apijavob.alif.tj/api/articles' \
--header 'Authorization: Bearer TOKEN