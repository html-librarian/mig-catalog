# Быстрый старт MIG Catalog API

## 🚀 Быстрая установка

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Настройка окружения
```bash
cp env.example .env
# Отредактируйте .env файл под ваши настройки
```

### 3. Настройка базы данных
```bash
# Проверка подключения
python test_db_connection.py

# Инициализация миграций (только при первом запуске)
python manage_migrations.py init

# Применение миграций
python manage_migrations.py upgrade
```

### 4. Запуск приложения
```bash
python run.py
```

## 📚 Документация API

После запуска приложения:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Основные команды

### Миграции базы данных
```bash
# Создать миграцию
python manage_migrations.py create "Описание изменений"

# Применить миграции
python manage_migrations.py upgrade

# Откатить миграцию
python manage_migrations.py downgrade

# Показать историю
python manage_migrations.py history
```

### Тестирование
```bash
# Запуск всех тестов
python -m pytest tests/ -v

# Запуск конкретного теста
python -m pytest tests/test_validators.py -v
```

## 🛡️ Безопасность

### Продакшен настройки
```bash
# В .env файле для продакшена:
ENVIRONMENT=production
SECRET_KEY=your-super-secret-key-here  # ОБЯЗАТЕЛЬНО измените!
```

## 📊 Мониторинг

### Логи
- Логи приложения: `logs/mig_catalog_YYYYMMDD.log`
- Логи миграций: выводятся в консоль

### Проверка состояния
```bash
# Проверка API
curl http://localhost:8000/health

# Проверка БД
python test_db_connection.py
```

## 🔍 Отладка

### Проблемы с подключением к БД
```bash
# Проверьте переменные окружения
echo $DATABASE_URL

# Проверьте подключение
python test_db_connection.py
```

### Проблемы с миграциями
```bash
# Показать текущую версию
python manage_migrations.py current

# Показать ожидающие миграции
python manage_migrations.py pending
```

## 📁 Структура проекта

```
backend/
├── app/                    # Основное приложение
│   ├── core/              # Основные компоненты
│   │   ├── auth.py        # Аутентификация
│   │   ├── cache.py       # Кэширование
│   │   ├── exceptions.py  # Обработка ошибок
│   │   ├── pagination.py  # Пагинация
│   │   └── validators.py  # Валидация
│   ├── users/             # Модуль пользователей
│   ├── catalog/           # Модуль товаров
│   ├── orders/            # Модуль заказов
│   └── news/              # Модуль новостей
├── migrations/            # Миграции БД
├── tests/                # Тесты
├── manage_migrations.py  # Скрипт управления миграциями
└── requirements.txt      # Зависимости
```

## 🎯 Основные улучшения v1.4

- ✅ **Безопасность**: Исправлена уязвимость SECRET_KEY
- ✅ **Миграции**: Система Alembic для управления БД
- ✅ **Тесты**: Комплексное тестирование
- ✅ **Кэширование**: Redis + fallback на память
- ✅ **Документация**: Детальная API документация
- ✅ **Пагинация**: Улучшенная система пагинации

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи в `logs/`
2. Убедитесь в корректности настроек в `.env`
3. Проверьте подключение к БД
4. Обратитесь к документации в `README.md` и `MIGRATIONS.md` 