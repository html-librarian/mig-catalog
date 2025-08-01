"""
Простой тест для проверки базовой функциональности
"""
import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent))

# Загружаем переменные окружения
load_dotenv()

# Устанавливаем тестовые переменные окружения
os.environ["ENVIRONMENT"] = "testing"
os.environ["DEBUG"] = "True"
os.environ[
    "SECRET_KEY"
] = "test-secret-key-64-characters-long-for-testing-purposes-only-123456789"


def test_environment_variables():
    """Тест загрузки переменных окружения"""
    # Проверяем, что основные переменные загружены
    assert os.getenv("ENVIRONMENT") == "testing"
    assert os.getenv("DEBUG") == "True"
    assert len(os.getenv("SECRET_KEY", "")) >= 64


def test_basic_imports():
    """Тест базовых импортов"""
    # Проверяем, что можем импортировать основные модули
    try:
        from app.core.validators import (
            EmailValidator,
            PasswordValidator,
            UsernameValidator,
        )

        assert PasswordValidator is not None
        assert EmailValidator is not None
        assert UsernameValidator is not None
    except ImportError as e:
        pytest.fail(f"Не удалось импортировать валидаторы: {e}")


def test_password_validation():
    """Тест валидации паролей"""
    from app.core.validators import PasswordValidator

    # Тест валидного пароля
    is_valid, errors = PasswordValidator.validate_password("StrongPass123!")
    assert is_valid, f"Пароль должен быть валидным: {errors}"

    # Тест невалидного пароля
    is_valid, errors = PasswordValidator.validate_password("weak")
    assert not is_valid, "Слабый пароль должен быть отклонен"


def test_email_validation():
    """Тест валидации email"""
    from app.core.validators import EmailValidator

    # Тест валидного email
    is_valid, errors = EmailValidator.validate_email("test@example.com")
    assert is_valid, f"Email должен быть валидным: {errors}"

    # Тест невалидного email
    is_valid, errors = EmailValidator.validate_email("invalid-email")
    assert not is_valid, "Невалидный email должен быть отклонен"


def test_username_validation():
    """Тест валидации имени пользователя"""
    from app.core.validators import UsernameValidator

    # Тест валидного имени пользователя
    is_valid, errors = UsernameValidator.validate_username("testuser")
    assert is_valid, f"Имя пользователя должно быть валидным: {errors}"

    # Тест невалидного имени пользователя
    is_valid, errors = UsernameValidator.validate_username("a")
    assert not is_valid, "Короткое имя пользователя должно быть отклонено"


if __name__ == "__main__":
    # Запуск тестов напрямую
    test_environment_variables()
    test_basic_imports()
    test_password_validation()
    test_email_validation()
    test_username_validation()
    print("✅ Все простые тесты прошли успешно!")
