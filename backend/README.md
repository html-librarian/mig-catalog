# 🚀 MIG Catalog Backend

<div align="center">

![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white)

**Современный FastAPI бэкенд для каталога товаров MIG**

[🚀 Быстрый старт](#-быстрый-старт) • [📚 Документация](#-документация) • [🧪 Тестирование](#-тестирование) • [🔒 Безопасность](#-безопасность)

</div>

---

## 📋 Содержание

- [🚀 Быстрый старт](#-быстрый-старт)
- [📚 Документация](#-документация)
- [🧪 Тестирование](#-тестирование)
- [🔒 Безопасность](#-безопасность)
- [🏗️ Архитектура](#️-архитектура)
- [🌐 API](#-api)

---

## 🚀 Быстрый старт

### 🐳 Docker (рекомендуется)

```bash
# Из корня проекта
docker-compose up -d
```

### 🐍 Локальная разработка

```bash
# Установка зависимостей
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate     # Windows

pip install -r requirements.txt

# Настройка базы данных
cp env.example .env
# Отредактируйте .env файл

# Генерация безопасных ключей
python generate_secrets.py

# Запуск миграций
python manage_migrations.py upgrade

# Запуск приложения
python run.py
```

### 🖥️ Доступные сервисы

| Сервис           | URL                          | Описание                    |
| ---------------- | ---------------------------- | --------------------------- |
| **API**          | http://localhost:8000        | Основной API сервер         |
| **Swagger UI**   | http://localhost:8000/docs   | Интерактивная документация  |
| **ReDoc**        | http://localhost:8000/redoc  | Альтернативная документация |
| **Health Check** | http://localhost:8000/health | Проверка состояния          |

---

## 📚 Документация

### 📖 Основная документация

- **[🚀 Быстрый старт](docs/QUICK_START.md)** - Полное руководство по запуску
- **[🏗️ Развертывание](docs/DEPLOYMENT.md)** - Продакшен развертывание
- **[🔒 Безопасность](docs/SECURITY.md)** - Документация по безопасности
- **[🧪 Тестирование](docs/TESTING.md)** - Руководство по тестированию
- **[🗄️ Миграции](docs/MIGRATIONS.md)** - Работа с базой данных
- **[🐛 Отладка](docs/VSCODE_DEBUG_GUIDE.md)** - Отладка в VS Code

### 📊 Отчеты и аналитика

- **[📈 Отчет об улучшениях](docs/IMPROVEMENTS_REPORT.md)** - Анализ улучшений
- **[📝 Финальный отчет](docs/FINAL_REPORT.md)** - Итоговый анализ проекта
- **[📋 Changelog](docs/CHANGELOG.md)** - История изменений

---

## 🧪 Тестирование

### 🚀 Быстрый запуск тестов

```bash
# Все тесты
make test

# Быстрые тесты
make test-fast

# Тесты безопасности
make test-security

# Тесты с покрытием
make test-coverage
```

### 🐍 Python скрипты

```bash
# Все тесты
python run_tests.py

# Быстрые тесты
python run_tests.py --fast

# Тесты безопасности
python run_tests.py --security
```

### 📊 Профили тестирования

```bash
# Быстрый профиль (~30 сек)
python test_profiles.py quick

# Профиль разработки (~2 мин)
python test_profiles.py development

# CI профиль (~5 мин)
python test_profiles.py ci
```

### 🧪 Ручное тестирование

```bash
# Запуск всех тестов
pytest tests/ -v

# Быстрые тесты
pytest tests/ -v -m "not slow"

# Тесты безопасности
pytest tests/test_security.py -v

# Покрытие кода
pytest tests/ --cov=app --cov-report=html
```

---

## 🔒 Безопасность

### ✅ Реализованные меры

- **🔐 JWT аутентификация** с улучшенной валидацией
- **🛡️ Rate limiting** с дифференцированными лимитами
- **🔒 Хеширование паролей** с bcrypt (14 раундов)
- **🛡️ Защита от XSS** и SQL инъекций
- **🚫 Черный список IP** для блокировки атак
- **📋 Заголовки безопасности** (HSTS, CSP, X-Frame-Options)
- **🔍 Валидация данных** с Pydantic
- **📊 Логирование безопасности** с маскированием чувствительных данных

### 🚨 Критические исправления

Все критические уязвимости безопасности были исправлены:

- ✅ **SECRET_KEY** - Безопасная генерация ключей
- ✅ **JWT валидация** - Полная проверка всех claims
- ✅ **HTTPS** - Настройки для продакшена
- ✅ **Защита от атак** - Комплексная система безопасности

**Статус безопасности**: 🟢 **9/10** (повышено с 6/10)

---

## 🏗️ Архитектура

### 📁 Структура проекта

```
backend/
├── 📁 app/                    # Код приложения
│   ├── 📁 catalog/           # Модуль товаров
│   │   ├── 📁 api/           # API эндпоинты
│   │   ├── 📁 models/        # Модели данных
│   │   ├── 📁 schemas/       # Pydantic схемы
│   │   └── 📁 services/      # Бизнес-логика
│   ├── 📁 users/             # Модуль пользователей
│   │   ├── 📁 api/           # API эндпоинты
│   │   ├── 📁 models/        # Модули данных
│   │   ├── 📁 schemas/       # Pydantic схемы
│   │   └── 📁 services/      # Бизнес-логика
│   ├── 📁 orders/            # Модуль заказов
│   │   ├── 📁 api/           # API эндпоинты
│   │   ├── 📁 models/        # Модели данных
│   │   ├── 📁 schemas/       # Pydantic схемы
│   │   └── 📁 services/      # Бизнес-логика
│   ├── 📁 news/              # Модуль новостей
│   │   ├── 📁 api/           # API эндпоинты
│   │   ├── 📁 models/        # Модели данных
│   │   ├── 📁 schemas/       # Pydantic схемы
│   │   └── 📁 services/      # Бизнес-логика
│   └── 📁 core/              # Общие компоненты
│       ├── 📄 auth.py        # Аутентификация
│       ├── 📄 config.py      # Конфигурация
│       ├── 📄 security.py    # Безопасность
│       ├── 📄 middleware.py  # Middleware
│       ├── 📄 logging.py     # Логирование
│       ├── 📄 cache.py       # Кэширование
│       ├── 📄 pagination.py  # Пагинация
│       ├── 📄 validators.py  # Валидация
│       ├── 📄 exceptions.py  # Исключения
│       ├── 📄 rate_limiter.py # Rate limiting
│       ├── 📄 schemas.py     # Общие схемы
│       └── 📄 dependencies.py # Зависимости
├── 📁 tests/                 # Тесты
│   ├── 📄 test_auth.py      # Тесты аутентификации
│   ├── 📄 test_security.py  # Тесты безопасности
│   ├── 📄 test_services.py  # Тесты сервисов
│   ├── 📄 test_validators.py # Тесты валидации
│   └── 📄 test_basic.py     # Базовые тесты
├── 📁 migrations/            # Миграции базы данных
│   ├── 📁 versions/         # Версии миграций
│   ├── 📄 env.py            # Конфигурация Alembic
│   └── 📄 script.py.mako    # Шаблон миграции
├── 📁 docs/                  # Документация
├── 📁 logs/                  # Логи приложения
├── 📄 requirements.txt       # Python зависимости
├── 📄 run.py                # Точка входа
├── 📄 main.py               # Основной файл приложения
├── 📄 generate_secrets.py   # Генерация ключей
└── 📄 README.md            # Документация
```

### 🏛️ Технологический стек

| Компонент            | Технология | Версия  | Назначение                  |
| -------------------- | ---------- | ------- | --------------------------- |
| **API Framework**    | FastAPI    | 0.109.0 | Современный веб-фреймворк   |
| **ORM**              | SQLAlchemy | 2.0.25  | Работа с базой данных       |
| **Database**         | PostgreSQL | 15      | Основная база данных        |
| **Cache**            | Redis      | 7       | Кэширование и rate limiting |
| **Authentication**   | JWT        | -       | Аутентификация              |
| **Validation**       | Pydantic   | 2.6.0   | Валидация данных            |
| **Testing**          | pytest     | 7.4.3   | Тестирование                |
| **Containerization** | Docker     | 3.8     | Контейнеризация             |

### 🏗️ Архитектурные принципы

- **🧩 Модульная архитектура** - Разделение на независимые модули
- **🔒 Безопасность по умолчанию** - Все меры безопасности включены
- **📊 Мониторинг** - Полное логирование и метрики
- **🧪 Тестирование** - Покрытие тестами всех компонентов
- **📈 Масштабируемость** - Готовность к росту нагрузки

---

## 🌐 API

### 🔐 Аутентификация

| Метод  | Endpoint                | Описание                          |
| ------ | ----------------------- | --------------------------------- |
| `POST` | `/api/v1/auth/register` | Регистрация пользователя          |
| `POST` | `/api/v1/auth/login`    | Вход в систему                    |
| `GET`  | `/api/v1/auth/me`       | Информация о текущем пользователе |
| `POST` | `/api/v1/auth/logout`   | Выход из системы                  |

### 👥 Пользователи

| Метод    | Endpoint               | Описание              |
| -------- | ---------------------- | --------------------- |
| `GET`    | `/api/v1/users/`       | Список пользователей  |
| `GET`    | `/api/v1/users/{uuid}` | Получить пользователя |
| `POST`   | `/api/v1/users/`       | Создать пользователя  |
| `PUT`    | `/api/v1/users/{uuid}` | Обновить пользователя |
| `DELETE` | `/api/v1/users/{uuid}` | Удалить пользователя  |

### 🛍️ Товары

| Метод    | Endpoint               | Описание       |
| -------- | ---------------------- | -------------- |
| `GET`    | `/api/v1/items/`       | Список товаров |
| `GET`    | `/api/v1/items/{uuid}` | Получить товар |
| `POST`   | `/api/v1/items/`       | Создать товар  |
| `PUT`    | `/api/v1/items/{uuid}` | Обновить товар |
| `DELETE` | `/api/v1/items/{uuid}` | Удалить товар  |

### 📦 Заказы

| Метод    | Endpoint                | Описание       |
| -------- | ----------------------- | -------------- |
| `GET`    | `/api/v1/orders/`       | Список заказов |
| `GET`    | `/api/v1/orders/{uuid}` | Получить заказ |
| `POST`   | `/api/v1/orders/`       | Создать заказ  |
| `PUT`    | `/api/v1/orders/{uuid}` | Обновить заказ |
| `DELETE` | `/api/v1/orders/{uuid}` | Удалить заказ  |

### 📰 Новости

| Метод    | Endpoint              | Описание        |
| -------- | --------------------- | --------------- |
| `GET`    | `/api/v1/news/`       | Список статей   |
| `GET`    | `/api/v1/news/{uuid}` | Получить статью |
| `POST`   | `/api/v1/news/`       | Создать статью  |
| `PUT`    | `/api/v1/news/{uuid}` | Обновить статью |
| `DELETE` | `/api/v1/news/{uuid}` | Удалить статью  |

### 🔍 Системные эндпоинты

| Метод | Endpoint           | Описание                         |
| ----- | ------------------ | -------------------------------- |
| `GET` | `/health`          | Базовая проверка состояния       |
| `GET` | `/health/detailed` | Детальная проверка всех сервисов |
| `GET` | `/metrics`         | Метрики производительности       |

---

## 🔧 Основные команды

### 🗄️ База данных

```bash
# Создание миграции
alembic revision --autogenerate -m "Description"

# Применение миграций
python manage_migrations.py upgrade

# Проверка подключения к БД
python test_db_connection.py
```

### 🔐 Безопасность

```bash
# Генерация безопасных ключей
python generate_secrets.py

# Проверка безопасности
pytest tests/test_security.py -v
```

### 🧪 Тестирование

```bash
# Все тесты
make test

# Быстрые тесты
make test-fast

# Тесты безопасности
make test-security

# Тесты с покрытием
make test-coverage
```

---

<div align="center">

**MIG Catalog Backend** - Современный FastAPI бэкенд

[🚀 Быстрый старт](#-быстрый-старт) • [📚 Документация](#-документация) • [🧪 Тестирование](#-тестирование) • [🔒 Безопасность](#-безопасность)

</div>
