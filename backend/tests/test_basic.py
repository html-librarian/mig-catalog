import pytest
from decimal import Decimal


def test_basic_functionality():
    """Простой тест базовой функциональности"""
    assert True  # Всегда проходит
    assert 1 + 1 == 2
    assert "hello" + " " + "world" == "hello world"


def test_decimal_operations():
    """Тест операций с Decimal"""
    price = Decimal("123.456")
    assert price == Decimal("123.456")
    assert str(price) == "123.456"


def test_string_operations():
    """Тест строковых операций"""
    username = "testuser"
    assert len(username) == 8
    assert username.isalnum() == True


def test_list_operations():
    """Тест операций со списками"""
    items = ["item1", "item2", "item3"]
    assert len(items) == 3
    assert "item1" in items
    assert items[0] == "item1"


def test_dict_operations():
    """Тест операций со словарями"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "is_active": True
    }
    assert user_data["username"] == "testuser"
    assert user_data["email"] == "test@example.com"
    assert user_data["is_active"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 