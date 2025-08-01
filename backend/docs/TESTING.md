# Руководство по тестированию MIG Catalog API

## 🧪 Обзор системы тестирования

Данный документ описывает различные способы запуска тестов в MIG Catalog API.

## 🚀 Быстрый старт

### Основные команды

```bash
# Все тесты
make test

# Быстрые тесты
make test-fast

# Тесты с покрытием
make test-coverage

# Справка
make help
```

### Python скрипты

```bash
# Все тесты
python run_tests.py

# Быстрые тесты
python run_tests.py --fast

# Тесты безопасности
python run_tests.py --security

# Тесты с покрытием
python run_tests.py --coverage
```

### Профили тестирования

```bash
# Быстрый профиль
python test_profiles.py quick

# Профиль разработки
python test_profiles.py development

# CI профиль
python test_profiles.py ci

# Профиль безопасности
python test_profiles.py security
```

## 📋 Типы тестов

### 1. Базовые тесты (`test_basic.py`)
- ✅ Простые unit тесты
- ✅ Проверка базовой функциональности
- ✅ Быстрое выполнение

```bash
make test-basic
python run_tests.py --basic
```

### 2. Тесты аутентификации (`test_auth.py`)
- ✅ Тесты регистрации и входа
- ✅ Проверка JWT токенов
- ✅ Валидация учетных данных

```bash
make test-auth
python run_tests.py --auth
```

### 3. Тесты безопасности (`test_security.py`)
- ✅ Защита от SQL injection
- ✅ Защита от XSS атак
- ✅ Валидация паролей
- ✅ Проверка email адресов
- ✅ Rate limiting

```bash
make test-security
python run_tests.py --security
```

### 4. Тесты валидации (`test_validators.py`)
- ✅ Валидация входных данных
- ✅ Проверка форматов
- ✅ Санитизация данных

```bash
make test-validators
python run_tests.py --validators
```

### 5. Тесты сервисов (`test_services.py`)
- ✅ Тесты бизнес-логики
- ✅ Mock тесты
- ✅ Интеграционные тесты

```bash
make test-services
python run_tests.py --services
```

## 🎯 Профили тестирования

### Quick Profile (Быстрый)
```bash
python test_profiles.py quick
```
- Время: ~30 секунд
- Критические тесты
- Базовые проверки

### Development Profile (Разработка)
```bash
python test_profiles.py development
```
- Время: ~2 минуты
- Основные тесты
- Проверка стиля кода
- Без медленных тестов

### CI Profile (CI/CD)
```bash
python test_profiles.py ci
```
- Время: ~5 минут
- Все тесты
- Покрытие кода
- Проверка безопасности
- Проверка типов

### Security Profile (Безопасность)
```bash
python test_profiles.py security
```
- Время: ~3 минуты
- Все тесты безопасности
- Сканирование кода
- Аудит зависимостей

### Full Profile (Полный)
```bash
python test_profiles.py full
```
- Время: ~10 минут
- Все тесты и проверки
- Полное покрытие
- Все инструменты качества

## 🛠️ Инструменты качества кода

### Linting (Flake8)
```bash
make lint
python run_tests.py --lint
```

### Сканирование безопасности (Bandit)
```bash
make security-scan
python run_tests.py --security-scan
```

### Проверка типов (MyPy)
```bash
make type-check
python run_tests.py --type-check
```

### Все проверки качества
```bash
make quality
```

## 📊 Покрытие кода

### Запуск с покрытием
```bash
make test-coverage
python run_tests.py --coverage
```

### Просмотр отчета
```bash
# HTML отчет
open htmlcov/index.html

# Консольный отчет
coverage report
```

### Минимальное покрытие
- Требуется: 70%
- Текущее: ~85%

## 🔧 Конфигурация

### pytest.ini
Основные настройки pytest находятся в `pytest.ini`:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
```

### Маркеры тестов
```python
import pytest

@pytest.mark.fast
def test_fast_function():
    pass

@pytest.mark.slow
def test_slow_function():
    pass

@pytest.mark.security
def test_security_function():
    pass
```

## 🐳 Docker тестирование

### Запуск тестов в Docker
```bash
make docker-test
```

### Сборка и тестирование
```bash
make docker-build
make docker-run
```

## 📈 Производительность

### Параллельное выполнение
```bash
python run_tests.py --parallel
```

### Профилирование
```bash
make profile
make analyze-profile
```

## 🔍 Отладка тестов

### Подробный вывод
```bash
python run_tests.py --verbose
pytest -v -s
```

### Остановка на первой ошибке
```bash
pytest -x
```

### Запуск конкретного теста
```bash
pytest tests/test_auth.py::test_register_user
```

### Запуск по маркеру
```bash
pytest -m fast
pytest -m "not slow"
```

## 🚨 CI/CD интеграция

### GitHub Actions
```yaml
- name: Run tests
  run: |
    make ci-test
```

### GitLab CI
```yaml
test:
  script:
    - make ci-test
```

### Jenkins
```groovy
stage('Test') {
    steps {
        sh 'make ci-test'
    }
}
```

## 📝 Написание тестов

### Структура теста
```python
import pytest
from app.core.validators import EmailValidator

class TestEmailValidator:
    def test_valid_email(self):
        """Тест валидного email"""
        assert EmailValidator.validate_email("test@example.com")
    
    def test_invalid_email(self):
        """Тест невалидного email"""
        assert not EmailValidator.validate_email("invalid-email")
```

### Фикстуры
```python
import pytest
from sqlalchemy.orm import Session

@pytest.fixture
def db_session():
    """Фикстура для сессии БД"""
    # Настройка
    session = create_test_session()
    yield session
    # Очистка
    session.close()
```

### Mock тесты
```python
from unittest.mock import Mock, patch

def test_service_with_mock():
    """Тест сервиса с моком"""
    mock_db = Mock()
    service = UserService(mock_db)
    
    # Настройка мока
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    # Тест
    result = service.get_user("test-id")
    assert result is None
```

## 🔧 Устранение неполадок

### Проблемы с зависимостями
```bash
make install
pip install -r requirements.txt
```

### Очистка кэша
```bash
make clean
```

### Проблемы с базой данных
```bash
make db-migrate
make db-reset
```

### Проблемы с Docker
```bash
make docker-clean
make docker-build
```

## 📚 Дополнительные ресурсы

- [pytest документация](https://docs.pytest.org/)
- [Coverage.py документация](https://coverage.readthedocs.io/)
- [Bandit документация](https://bandit.readthedocs.io/)
- [MyPy документация](https://mypy.readthedocs.io/)

## 🤝 Вклад в тестирование

### Добавление нового теста
1. Создайте файл `tests/test_<module>.py`
2. Добавьте соответствующие маркеры
3. Запустите тесты локально
4. Добавьте в CI/CD

### Добавление нового профиля
1. Добавьте метод в `TestProfiles`
2. Обновите документацию
3. Протестируйте профиль

### Улучшение покрытия
1. Запустите `make test-coverage`
2. Найдите непокрытые строки
3. Добавьте тесты для непокрытого кода
4. Проверьте покрытие снова 