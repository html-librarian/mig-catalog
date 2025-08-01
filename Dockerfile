# Dockerfile для MIG Catalog Backend
FROM python:3.9-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY backend/requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY backend/ .

# Создание пользователя для безопасности
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app

# Делаем скрипт исполняемым
RUN chmod +x docker-entrypoint.sh

USER appuser

# Открытие порта
EXPOSE 8000

# Команда запуска
CMD ["./docker-entrypoint.sh"] 