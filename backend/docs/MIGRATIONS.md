# Управление миграциями базы данных

## Обзор

Проект использует Alembic для управления миграциями базы данных. Это позволяет безопасно изменять схему базы данных в продакшене.

## Быстрый старт

### 1. Инициализация (только при первом запуске)

```bash
# Инициализировать миграции
python manage_migrations.py init
```

### 2. Создание миграции

```bash
# Создать миграцию на основе изменений в моделях
python manage_migrations.py create "Описание изменений"
```

### 3. Применение миграций

```bash
# Обновить базу данных до последней версии
python manage_migrations.py upgrade
```

## Команды управления

### Создание миграций

```bash
# Автоматическое создание миграции
python manage_migrations.py create "Add user table"

# Ручное создание пустой миграции
alembic revision -m "Manual migration"
```

### Применение миграций

```bash
# Обновить до последней версии
python manage_migrations.py upgrade

# Обновить до конкретной версии
alembic upgrade 001

# Обновить на N версий вперед
alembic upgrade +2
```

### Откат миграций

```bash
# Откатить на одну версию назад
python manage_migrations.py downgrade

# Откатить до конкретной версии
python manage_migrations.py downgrade 001

# Откатить на N версий назад
alembic downgrade -2
```

### Просмотр информации

```bash
# Показать историю миграций
python manage_migrations.py history

# Показать текущую версию
python manage_migrations.py current

# Показать ожидающие миграции
python manage_migrations.py pending
```

## Структура миграций

```
migrations/
├── env.py              # Настройки окружения
├── script.py.mako      # Шаблон для миграций
└── versions/           # Файлы миграций
    ├── 001_initial_migration.py
    ├── 002_add_user_fields.py
    └── ...
```

## Лучшие практики

### 1. Именование миграций

Используйте описательные имена:
- ✅ `Add user authentication fields`
- ✅ `Create order items table`
- ❌ `Update table`
- ❌ `Fix bug`

### 2. Размер миграций

- Делайте миграции атомарными
- Одна миграция = одно логическое изменение
- Избегайте больших миграций с множественными изменениями

### 3. Обратная совместимость

- Всегда проверяйте возможность отката
- Тестируйте миграции на тестовой базе данных
- Делайте бэкапы перед применением в продакшене

### 4. Безопасность данных

```python
# Пример безопасной миграции
def upgrade():
    # Добавляем новое поле с дефолтным значением
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))

def downgrade():
    # Удаляем поле при откате
    op.drop_column('users', 'is_active')
```

## Работа в команде

### 1. Создание миграции

```bash
# 1. Внесите изменения в модели
# 2. Создайте миграцию
python manage_migrations.py create "Add new feature"

# 3. Проверьте сгенерированную миграцию
cat migrations/versions/XXX_add_new_feature.py

# 4. Примените миграцию локально
python manage_migrations.py upgrade

# 5. Зафиксируйте изменения в git
git add migrations/versions/XXX_add_new_feature.py
git commit -m "Add migration for new feature"
```

### 2. Применение миграций в продакшене

```bash
# 1. Подключитесь к продакшен серверу
# 2. Остановите приложение
# 3. Сделайте бэкап базы данных
pg_dump myapp > backup.sql

# 4. Примените миграции
python manage_migrations.py upgrade

# 5. Запустите приложение
# 6. Проверьте работоспособность
```

## Устранение проблем

### Ошибка "Target database is not up to date"

```bash
# Проверьте текущую версию
python manage_migrations.py current

# Примените все миграции
python manage_migrations.py upgrade
```

### Конфликт миграций

```bash
# 1. Откатитесь к общей версии
python manage_migrations.py downgrade <common_revision>

# 2. Примените миграции заново
python manage_migrations.py upgrade
```

### Проблемы с подключением к БД

```bash
# Проверьте переменные окружения
echo $DATABASE_URL

# Проверьте подключение
python test_db_connection.py
```

## Мониторинг

### Проверка состояния

```bash
# Текущая версия
python manage_migrations.py current

# Ожидающие миграции
python manage_migrations.py pending

# История миграций
python manage_migrations.py history
```

### Логирование

Миграции логируются в стандартный вывод. Для продакшена рекомендуется перенаправлять логи в файл:

```bash
python manage_migrations.py upgrade > migration.log 2>&1
```

## Интеграция с CI/CD

### GitHub Actions

```yaml
- name: Run migrations
  run: |
    python manage_migrations.py upgrade
```

### Docker

```dockerfile
# В Dockerfile
COPY migrations/ /app/migrations/
RUN python manage_migrations.py upgrade
```

## Полезные команды

```bash
# Показать SQL для миграции
alembic upgrade head --sql

# Проверить миграцию без применения
alembic check

# Создать пустую миграцию
alembic revision -m "Empty migration"

# Показать информацию о миграции
alembic show 001
``` 