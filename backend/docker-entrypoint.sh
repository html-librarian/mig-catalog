#!/bin/bash

# Скрипт запуска для Docker контейнера
set -e

echo "🚀 Запуск MIG Catalog Backend в Docker..."

# Ожидание готовности базы данных
echo "⏳ Ожидание готовности базы данных..."
until pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
  echo "База данных недоступна, ожидание..."
  sleep 2
done

echo "✅ База данных готова!"

# Применение миграций
echo "📦 Применение миграций..."
python manage_migrations.py upgrade

# Запуск приложения
echo "🚀 Запуск FastAPI приложения..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 