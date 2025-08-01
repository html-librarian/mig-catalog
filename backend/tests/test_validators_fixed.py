import pytest
from fastapi.testclient import TestClient

from app.core.validators import (
    EmailValidator,
    PasswordValidator,
    UsernameValidator,
    validate_uuid,
    validate_uuid_optional,
)
from app.main import app

client = TestClient(app)


class TestPasswordValidator:
    """Тесты для валидации паролей"""

    def test_valid_password(self):
        """Тест валидного пароля"""
        is_valid, errors = PasswordValidator.validate_password("Password123!")
        assert is_valid
        is_valid, errors = PasswordValidator.validate_password("MyPass123!")
        assert is_valid
        is_valid, errors = PasswordValidator.validate_password(
            "SecurePass2024!"
        )
        assert is_valid

    def test_invalid_password_too_short(self):
        """Тест слишком короткого пароля"""
        is_valid, errors = PasswordValidator.validate_password("Pass1")
        assert not is_valid

    def test_invalid_password_no_letters(self):
        """Тест пароля без букв"""
        is_valid, errors = PasswordValidator.validate_password("12345678")
        assert not is_valid

    def test_invalid_password_no_digits(self):
        """Тест пароля без цифр"""
        is_valid, errors = PasswordValidator.validate_password("Password")
        assert not is_valid

    def test_password_requirements(self):
        """Тест получения требований к паролю"""
        requirements = PasswordValidator.get_password_requirements()
        assert "8 символов" in requirements
        assert "букву" in requirements
        assert "цифру" in requirements


class TestEmailValidator:
    """Тесты для валидации email"""

    def test_valid_emails(self):
        """Тест валидных email адресов"""
        # Используем тестовые домены
        valid_emails = [
            "test@test.com",
            "user.name@test.co.uk",
            "user+tag@test.org",
            "123@test.ru",
        ]
        for email in valid_emails:
            is_valid, errors = EmailValidator.validate_email(email)
            assert is_valid

    def test_invalid_emails(self):
        """Тест невалидных email адресов"""
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user@.com",
            "user..name@example.com",
        ]
        for email in invalid_emails:
            is_valid, errors = EmailValidator.validate_email(email)
            assert not is_valid


class TestUsernameValidator:
    """Тесты для валидации имен пользователей"""

    def test_valid_usernames(self):
        """Тест валидных имен пользователей"""
        valid_usernames = ["user123", "my_user", "TestUser", "user_123"]
        for username in valid_usernames:
            is_valid, errors = UsernameValidator.validate_username(username)
            assert is_valid

    def test_invalid_usernames(self):
        """Тест невалидных имен пользователей"""
        invalid_usernames = [
            "ab",  # слишком короткое
            "very_long_username_that_exceeds_limit",  # слишком длинное
            "user-name",  # содержит дефис
            "user.name",  # содержит точку
            "user name",  # содержит пробел
            "",  # пустое
        ]
        for username in invalid_usernames:
            is_valid, errors = UsernameValidator.validate_username(username)
            assert not is_valid


class TestUUIDValidator:
    """Тесты для валидации UUID"""

    def test_valid_uuid(self):
        """Тест валидного UUID"""
        valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
        result = validate_uuid(valid_uuid, "UUID")
        assert result == valid_uuid

    def test_invalid_uuid(self):
        """Тест невалидного UUID"""
        invalid_uuid = "invalid-uuid"
        with pytest.raises(ValueError) as exc_info:
            validate_uuid(invalid_uuid, "UUID")
        assert "UUID имеет неверный формат" in str(exc_info.value)

    def test_optional_uuid_none(self):
        """Тест опционального UUID с None"""
        result = validate_uuid_optional(None, "UUID")
        assert result is None

    def test_optional_uuid_valid(self):
        """Тест опционального UUID с валидным значением"""
        valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
        result = validate_uuid_optional(valid_uuid, "UUID")
        assert result == valid_uuid

    def test_optional_uuid_invalid(self):
        """Тест опционального UUID с невалидным значением"""
        invalid_uuid = "invalid-uuid"
        with pytest.raises(ValueError) as exc_info:
            validate_uuid_optional(invalid_uuid, "UUID")
        assert "UUID имеет неверный формат" in str(exc_info.value)
