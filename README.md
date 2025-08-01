# 🛍️ MIG Catalog API

<div align="center">

![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-3.8-2496ED?style=for-the-badge&logo=docker&logoColor=white)

**Полнофункциональный каталог товаров с современным API на FastAPI**

[🚀 Быстрый старт](#-быстрый-старт) • [📚 Документация](#-документация) • [🔒 Безопасность](#-безопасность) • [🛠️ Разработка](#️-разработка) • [📊 API](#-api)

</div>

---

## 📋 Содержание

- [🚀 Быстрый старт](#-быстрый-старт)
- [📚 Документация](#-документация)
- [🔒 Безопасность](#-безопасность)
- [🛠️ Разработка](#️-разработка)
- [📊 API](#-api)
- [🏗️ Архитектура](#️-архитектура)
- [📈 Мониторинг](#-мониторинг)
- [🤝 Вклад в проект](#-вклад-в-проект)

---

## 🚀 Быстрый старт

### Предварительные требования

- **Docker** и **Docker Compose** (для быстрого запуска)
- **Python 3.9+** (для разработки)
- **PostgreSQL 15+** (для продакшена)
- **Redis 7+** (для кэширования)

### 🐳 Запуск с Docker (рекомендуется)

```bash
# Клонирование репозитория
git clone <repository-url>
cd mig-catalog

# Запуск всех сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps
```

### 🖥️ Доступные сервисы

| Сервис               | URL                          | Описание                    |
| -------------------- | ---------------------------- | --------------------------- |
| **Backend API**      | http://localhost:8000        | Основной API сервер         |
| **API Документация** | http://localhost:8000/docs   | Swagger UI                  |
| **ReDoc**            | http://localhost:8000/redoc  | Альтернативная документация |
| **Health Check**     | http://localhost:8000/health | Проверка состояния          |
| **База данных**      | localhost:5432               | PostgreSQL                  |
| **Redis**            | localhost:6379               | Кэширование                 |

### 🛑 Остановка приложения

```bash
docker-compose down
```

---

## 📚 Документация

### 📖 Основная документация

- **[🐛 Отладка в VS Code](VSCODE_DEBUG_GUIDE.md)** - Руководство по отладке
- **[📋 История изменений](CHANGELOG.md)** - Changelog проекта
- **[🔒 Безопасность](backend/app/core/security.py)** - Модуль безопасности
- **[🧪 Тестирование](backend/tests/)** - Тесты проекта
- **[🗄️ Миграции](backend/migrations/)** - Миграции базы данных

### 📊 Отчеты и аналитика

- **[📈 Отчет об улучшениях](backend/IMPROVEMENTS_SUMMARY.md)** - Анализ улучшений
- **[🔐 Отчет по безопасности](backend/SECURITY_FIXES_REPORT.md)** - Исправленные уязвимости

---

## 🔒 Безопасность

### ✅ Реализованные меры безопасности

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

## 🛠️ Разработка

### 🐍 Локальная разработка

```bash
# Установка зависимостей
cd backend
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

### 🧪 Тестирование

```bash
# Все тесты
pytest tests/ -v

# Быстрые тесты
pytest tests/ -v -m "not slow"

# Тесты безопасности
pytest tests/test_security.py -v

# Покрытие кода
pytest tests/ --cov=app --cov-report=html
```

### 🏗️ Структура проекта

```
mig-catalog/
├── 📁 backend/                 # Backend API (FastAPI)
│   ├── 📁 app/                # Код приложения
│   │   ├── 📁 catalog/        # Модуль товаров
│   │   ├── 📁 users/          # Модуль пользователей
│   │   ├── 📁 orders/         # Модуль заказов
│   │   ├── 📁 news/           # Модуль новостей
│   │   └── 📁 core/           # Общие компоненты
│   ├── 📁 tests/              # Тесты
│   ├── 📁 migrations/         # Миграции базы данных
│   └── 📄 requirements.txt    # Python зависимости
├── 📁 frontend/               # Frontend (будущее)
├── 📄 docker-compose.yml      # Docker Compose конфигурация
├── 📄 Dockerfile              # Dockerfile для backend
├── 📄 CHANGELOG.md           # История изменений
├── 📄 VSCODE_DEBUG_GUIDE.md  # Руководство по отладке
└── 📄 README.md              # Документация
```

---

## 📊 API

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
| `GET` | `/alerts`          | Активные алерты                  |
| `GET` | `/status`          | Полный статус системы            |

---

## 🏗️ Архитектура

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

## 📈 Мониторинг

### 📊 Метрики

- **Системные метрики**: CPU, память, диск
- **Метрики базы данных**: Пул соединений, производительность
- **Метрики приложения**: Время ответа, количество запросов
- **Метрики безопасности**: Неудачные попытки входа, заблокированные IP

### 📝 Логирование

- **Структурированные логи** в JSON формате
- **Correlation ID** для трассировки запросов
- **Маскирование чувствительных данных**
- **Различные уровни логирования** (DEBUG, INFO, WARNING, ERROR)

### 🔍 Health Checks

- **Базовая проверка**: `/health`
- **Детальная проверка**: `/health/detailed`
- **Проверка базы данных**
- **Проверка Redis**
- **Проверка переменных окружения**

---

## 🚀 Продакшн развертывание

### 🔧 Настройка продакшена

```bash
# Генерация безопасных ключей
cd backend
python generate_secrets.py

# Настройка продакшена
sudo ./setup_production.sh
```

### 🛡️ Рекомендации для продакшена

1. **🔐 Измените все дефолтные пароли**
2. **🔒 Настройте HTTPS** через reverse proxy (nginx)
3. **🛡️ Настройте firewall** и ограничьте доступ
4. **📊 Настройте мониторинг** и алерты
5. **💾 Создайте бэкапы** базы данных
6. **🔄 Настройте CI/CD** для автоматического деплоя

---

## 🤝 Вклад в проект

### 📋 Процесс разработки

1. **Fork** репозитория
2. Создайте **feature branch**: `git checkout -b feature/amazing-feature`
3. Внесите изменения и **добавьте тесты**
4. **Запустите тесты**: `pytest tests/ -v`
5. **Создайте Pull Request**

### 🧪 Тестирование

```bash
# Запуск всех тестов
make test

# Быстрые тесты
make test-fast

# Тесты безопасности
make test-security

# Тесты с покрытием
make test-coverage
```

### 📝 Стандарты кода

- **Python**: PEP 8, type hints
- **Документация**: docstrings, README файлы
- **Тестирование**: pytest, coverage > 80%
- **Безопасность**: Все тесты безопасности должны проходить

---

## 📄 Лицензия

Этот проект распространяется под лицензией **MIT License**.

---

<div align="center">

**MIG Catalog API** - Современный каталог товаров с API на FastAPI

[🚀 Быстрый старт](#-быстрый-старт) • [📚 Документация](#-документация) • [🔒 Безопасность](#-безопасность) • [🛠️ Разработка](#️-разработка)

</div>
