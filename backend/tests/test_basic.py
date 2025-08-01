"""
Базовый тест для проверки окружения
"""

import os
import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent))

# Устанавливаем переменные окружения
os.environ["ENVIRONMENT"] = "testing"
os.environ["DEBUG"] = "True"
os.environ[
    "SECRET_KEY"
] = "test-secret-key-64-characters-long-for-testing-purposes-only-123456789"


def test_environment():
    """Тест переменных окружения"""
    assert os.getenv("ENVIRONMENT") == "testing"
    assert os.getenv("DEBUG") == "True"
    assert len(os.getenv("SECRET_KEY", "")) >= 64
    print("✅ Переменные окружения настроены правильно")


def test_validators_import():
    """Тест импорта валидаторов"""
    try:
        # Импортируем только валидаторы, избегая циклических импортов
        from app.core.validators import (
            EmailValidator,
            PasswordValidator,
            UsernameValidator,
        )

        # Тестируем валидацию пароля
        is_valid, errors = PasswordValidator.validate_password(
            "StrongPass123!"
        )
        assert is_valid, f"Пароль должен быть валидным: {errors}"

        # Тестируем валидацию email
        is_valid, errors = EmailValidator.validate_email("test@example.com")
        assert is_valid, f"Email должен быть валидным: {errors}"

        # Тестируем валидацию имени пользователя
        is_valid, errors = UsernameValidator.validate_username("testuser")
        assert is_valid, f"Имя пользователя должно быть валидным: {errors}"

        print("✅ Валидаторы работают правильно")

    except Exception as e:
        print(f"❌ Ошибка при тестировании валидаторов: {e}")
        raise


if __name__ == "__main__":
    print("🚀 Запуск базовых тестов...")
    test_environment()
    test_validators_import()
    print("✅ Все базовые тесты прошли успешно!")
