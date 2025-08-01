import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.validators import (
    PasswordValidator, 
    EmailValidator, 
    PriceValidator, 
    UsernameValidator,
    DataValidator,
    validate_uuid,
    validate_uuid_optional
)
from decimal import Decimal
from fastapi import HTTPException

client = TestClient(app)


class TestPasswordValidator:
    """Тесты для валидации паролей"""
    
    def test_valid_password(self):
        """Тест валидного пароля"""
        assert PasswordValidator.validate_password("Password123!") == True
        assert PasswordValidator.validate_password("MyPass123!") == True
        assert PasswordValidator.validate_password("SecurePass2024!") == True
    
    def test_invalid_password_too_short(self):
        """Тест слишком короткого пароля"""
        assert PasswordValidator.validate_password("Pass1") == False
    
    def test_invalid_password_no_letters(self):
        """Тест пароля без букв"""
        assert PasswordValidator.validate_password("12345678") == False
    
    def test_invalid_password_no_digits(self):
        """Тест пароля без цифр"""
        assert PasswordValidator.validate_password("Password") == False
    
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
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "123@test.ru"
        ]
        for email in valid_emails:
            assert EmailValidator.validate_email(email) == True
    
    def test_invalid_emails(self):
        """Тест невалидных email адресов"""
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user@.com",
            "user..name@example.com"
        ]
        for email in invalid_emails:
            assert EmailValidator.validate_email(email) == False


class TestPriceValidator:
    """Тесты для валидации цен"""
    
    def test_valid_prices(self):
        """Тест валидных цен"""
        valid_prices = [
            Decimal("10.50"),
            Decimal("0.01"),
            Decimal("999999.99"),
            Decimal("100")
        ]
        for price in valid_prices:
            assert PriceValidator.validate_price(price) == True
    
    def test_invalid_prices(self):
        """Тест невалидных цен"""
        invalid_prices = [
            Decimal("0"),
            Decimal("-10.50"),
            Decimal("1000000.00"),
            Decimal("999999.999")
        ]
        for price in invalid_prices:
            assert PriceValidator.validate_price(price) == False
    
    def test_price_formatting(self):
        """Тест форматирования цен"""
        price = Decimal("123.456")
        formatted = PriceValidator.format_price(price)
        assert formatted == "123.46"


class TestUsernameValidator:
    """Тесты для валидации имен пользователей"""
    
    def test_valid_usernames(self):
        """Тест валидных имен пользователей"""
        valid_usernames = [
            "user123",
            "my_user",
            "TestUser",
            "user_123"
        ]
        for username in valid_usernames:
            assert UsernameValidator.validate_username(username) == True
    
    def test_invalid_usernames(self):
        """Тест невалидных имен пользователей"""
        invalid_usernames = [
            "ab",  # слишком короткое
            "very_long_username_that_exceeds_limit",  # слишком длинное
            "user-name",  # содержит дефис
            "user.name",  # содержит точку
            "user name",  # содержит пробел
            ""  # пустое
        ]
        for username in invalid_usernames:
            assert UsernameValidator.validate_username(username) == False


class TestDataValidator:
    """Тесты для валидации данных"""
    
    def test_valid_item_data(self):
        """Тест валидных данных товара"""
        is_valid, error = DataValidator.validate_item_data(
            name="Test Item",
            price=Decimal("10.50"),
            category="Electronics"
        )
        assert is_valid == True
        assert error is None
    
    def test_invalid_item_data(self):
        """Тест невалидных данных товара"""
        # Слишком короткое название
        is_valid, error = DataValidator.validate_item_data(
            name="A",
            price=Decimal("10.50"),
            category="Electronics"
        )
        assert is_valid == False
        assert "2 символа" in error
        
        # Невалидная цена
        is_valid, error = DataValidator.validate_item_data(
            name="Test Item",
            price=Decimal("-10.50"),
            category="Electronics"
        )
        assert is_valid == False
        assert "положительной" in error
    
    def test_valid_user_data(self):
        """Тест валидных данных пользователя"""
        is_valid, error = DataValidator.validate_user_data(
            email="test@example.com",
            username="testuser",
            password="Password123!"
        )
        assert is_valid == True
        assert error is None
    
    def test_invalid_user_data(self):
        """Тест невалидных данных пользователя"""
        # Невалидный email
        is_valid, error = DataValidator.validate_user_data(
            email="invalid-email",
            username="testuser",
            password="Password123"
        )
        assert is_valid == False
        assert "email" in error
        
        # Невалидный пароль
        is_valid, error = DataValidator.validate_user_data(
            email="test@example.com",
            username="testuser",
            password="123"
        )
        assert is_valid == False
        assert "8 символов" in error


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
        with pytest.raises(HTTPException) as exc_info:
            validate_uuid(invalid_uuid, "UUID")
        assert exc_info.value.status_code == 400
        assert "Неверный формат" in exc_info.value.detail
    
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
        with pytest.raises(HTTPException) as exc_info:
            validate_uuid_optional(invalid_uuid, "UUID")
        assert exc_info.value.status_code == 400 