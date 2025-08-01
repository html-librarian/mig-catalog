# Инструкции по развертыванию

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Настройка базы данных

```bash
# Создание .env файла
cp env.example .env

# Редактирование .env файла
# Укажите правильные параметры подключения к БД

# Инициализация базы данных
python init_database.py
```

### 3. Запуск приложения

```bash
# Режим разработки
python run.py

# Продакшн режим
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🔧 Настройка окружения

### Переменные окружения

Создайте файл `.env` на основе `env.example`:

```env
# Настройки приложения
APP_NAME=MIG Catalog API
APP_VERSION=1.2.0
DEBUG=False

# Настройки сервера
HOST=0.0.0.0
PORT=8000

# Настройки базы данных
DATABASE_URL=postgresql://user:password@localhost/mig_catalog

# Настройки Redis
REDIS_URL=redis://localhost:6379

# Настройки безопасности
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Настройки CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Настройки логирования
LOG_LEVEL=INFO
```

### Требования к системе

- Python 3.9+
- PostgreSQL 12+
- Redis 6+ (опционально, для кэширования)

## 🐳 Docker развертывание

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db/mig_catalog
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=mig_catalog
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine

volumes:
  postgres_data:
```

## 🔒 Безопасность

### Продакшн настройки

1. **Измените SECRET_KEY** на уникальный секретный ключ
2. **Настройте CORS** для ваших доменов
3. **Отключите DEBUG** режим
4. **Настройте HTTPS** через reverse proxy (nginx)
5. **Ограничьте доступ** к базе данных

### Рекомендуемые настройки

```env
DEBUG=False
SECRET_KEY=your-very-long-and-random-secret-key
ALLOWED_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
LOG_LEVEL=WARNING
```

## 📊 Мониторинг

### Логи

Логи сохраняются в папке `logs/`:
- `mig_catalog_YYYYMMDD.log` - ежедневные логи
- Консольный вывод для разработки

### Health Check

```bash
curl http://localhost:8000/health
```

### Метрики

- Время ответа API
- Количество запросов
- Ошибки и исключения
- Использование памяти

## 🔄 Обновление

### Процесс обновления

1. Остановите приложение
2. Создайте бэкап базы данных
3. Обновите код
4. Запустите миграции (если есть)
5. Перезапустите приложение

### Миграции

```bash
# Создание миграции
alembic revision --autogenerate -m "Description"

# Применение миграций
alembic upgrade head
```

## 🧪 Тестирование

### Запуск тестов

```bash
# Установка pytest
pip install pytest

# Запуск тестов
pytest tests/

# С покрытием
pytest --cov=app tests/
```

### Тестовое окружение

```bash
# Создание тестовой БД
python init_database.py --test

# Запуск тестов
DATABASE_URL=postgresql://user:password@localhost/mig_catalog_test pytest
``` 