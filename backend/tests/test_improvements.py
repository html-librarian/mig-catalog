"""
Тесты для улучшений системы
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.cache import cache_manager
from app.core.monitoring import (
    alert_manager,
    health_checker,
    performance_monitor,
)
from app.core.validators import (
    EmailValidator,
    PasswordValidator,
    UsernameValidator,
    sanitize_input,
    validate_item_data,
)
from app.main import app

client = TestClient(app)


class TestImprovedValidation:
    """Тесты улучшенной валидации"""

    def test_item_validation_success(self):
        """Тест успешной валидации товара"""
        is_valid, errors = validate_item_data(
            name="Test Item", price=100.50, category="Electronics"
        )
        assert is_valid
        assert len(errors) == 0

    def test_item_validation_failure(self):
        """Тест неудачной валидации товара"""
        # Пустое название
        is_valid, errors = validate_item_data("", 100.50, "Electronics")
        assert not is_valid
        assert "пустым" in errors[0]

        # Отрицательная цена
        is_valid, errors = validate_item_data(
            "Test Item", -10.0, "Electronics"
        )
        assert not is_valid
        assert "отрицательной" in errors[0]

        # Слишком высокая цена
        is_valid, errors = validate_item_data(
            "Test Item", 100000000.0, "Electronics"
        )
        assert not is_valid
        assert "превышать" in errors[0]

    def test_password_validation_improved(self):
        """Тест улучшенной валидации паролей"""
        # Сильный пароль
        is_valid, errors = PasswordValidator.validate_password(
            "StrongPass123!"
        )
        assert is_valid
        assert len(errors) == 0

        # Слабый пароль - только цифры
        is_valid, errors = PasswordValidator.validate_password("12345678")
        assert not is_valid
        assert any("букву" in error for error in errors)

        # Простой пароль
        is_valid, errors = PasswordValidator.validate_password("password")
        assert not is_valid
        assert any("простой" in error for error in errors)

        # Слишком длинный пароль
        long_password = "a" * 129
        is_valid, errors = PasswordValidator.validate_password(long_password)
        assert not is_valid
        assert any("превышать" in error for error in errors)

    def test_email_validation_improved(self):
        """Тест улучшенной валидации email"""
        # Валидный email
        is_valid, errors = EmailValidator.validate_email("test@example.com")
        assert is_valid
        assert len(errors) == 0

        # Одноразовый email
        is_valid, errors = EmailValidator.validate_email(
            "test@10minutemail.com"
        )
        assert not is_valid
        assert any("одноразовых" in error for error in errors)

        # Слишком длинный email
        long_email = "a" * 250 + "@example.com"
        is_valid, errors = EmailValidator.validate_email(long_email)
        assert not is_valid
        assert any("превышать" in error for error in errors)

    def test_username_validation_improved(self):
        """Тест улучшенной валидации имени пользователя"""
        # Валидное имя
        is_valid, errors = UsernameValidator.validate_username("testuser123")
        assert is_valid
        assert len(errors) == 0

        # Зарезервированное имя
        is_valid, errors = UsernameValidator.validate_username("admin")
        assert not is_valid
        assert any("зарезервировано" in error for error in errors)

        # Слишком короткое имя
        is_valid, errors = UsernameValidator.validate_username("ab")
        assert not is_valid
        assert any("минимум" in error for error in errors)


class TestInputSanitization:
    """Тесты очистки входных данных"""

    def test_sanitize_input_basic(self):
        """Базовый тест очистки входных данных"""
        malicious_input = "<script>alert('xss')</script>"
        sanitized = sanitize_input(malicious_input)
        assert "<" not in sanitized
        assert ">" not in sanitized
        assert "script" not in sanitized

    def test_sanitize_input_sql_injection(self):
        """Тест очистки SQL инъекций"""
        sql_injection = "'; DROP TABLE users; --"
        sanitized = sanitize_input(sql_injection)
        assert "'" not in sanitized
        assert ";" not in sanitized

    def test_sanitize_input_length_limit(self):
        """Тест ограничения длины"""
        long_input = "a" * 2000
        sanitized = sanitize_input(long_input, max_length=100)
        assert len(sanitized) <= 100


class TestCaching:
    """Тесты кэширования"""

    def test_cache_basic_operations(self):
        """Базовые операции кэша"""
        # Тест установки значения
        success = cache_manager.set("test_key", {"data": "test_value"}, ttl=60)
        assert success

        # Тест получения значения
        value = cache_manager.get("test_key")
        assert value == {"data": "test_value"}

        # Тест удаления значения
        success = cache_manager.delete("test_key")
        assert success

        # Проверяем, что значение удалено
        value = cache_manager.get("test_key")
        assert value is None

    def test_cache_pattern_deletion(self):
        """Тест удаления по паттерну"""
        # Устанавливаем несколько значений
        cache_manager.set("user:1", "data1")
        cache_manager.set("user:2", "data2")
        cache_manager.set("item:1", "data3")

        # Удаляем все значения user:*
        deleted_count = cache_manager.delete_pattern("user:*")
        assert deleted_count >= 2

        # Проверяем, что user значения удалены
        assert cache_manager.get("user:1") is None
        assert cache_manager.get("user:2") is None

        # Проверяем, что item значения остались
        assert cache_manager.get("item:1") is not None


class TestMonitoring:
    """Тесты мониторинга"""

    def test_performance_monitor(self):
        """Тест монитора производительности"""
        # Записываем метрики
        performance_monitor.record_request("/test", "GET", 200, 0.1)
        performance_monitor.record_request("/test", "GET", 404, 0.2)

        # Получаем метрики
        metrics = performance_monitor.get_metrics()

        assert "system" in metrics
        assert "application" in metrics
        assert "endpoints" in metrics

        # Проверяем, что метрики записаны
        assert metrics["application"]["total_requests"] >= 2
        assert metrics["application"]["total_errors"] >= 1

    def test_health_checker(self):
        """Тест проверки здоровья"""

        # Регистрируем тестовую проверку
        def test_check():
            return True

        health_checker.register_check("test_check", test_check)

        # Запускаем проверки
        health_status = health_checker.run_health_checks()

        assert "status" in health_status
        assert "checks" in health_status
        assert "test_check" in health_status["checks"]
        assert health_status["checks"]["test_check"]["status"] == "healthy"

    def test_alert_manager(self):
        """Тест менеджера алертов"""
        # Создаем тестовые метрики с высоким CPU
        test_metrics = {
            "system": {
                "cpu_percent": 85,  # Выше порога 80%
                "memory_percent": 70,
                "disk_percent": 75,
            },
            "application": {
                "error_rate_percent": 3,
                "avg_response_times": {"/slow": 2.5},  # Выше порога 2.0s
            },
        }

        # Проверяем алерты
        alerts = alert_manager.check_alerts(test_metrics)

        # Должен быть алерт на высокий CPU
        cpu_alerts = [a for a in alerts if a["metric"] == "cpu_percent"]
        assert len(cpu_alerts) > 0

        # Должен быть алерт на медленный ответ
        response_alerts = [a for a in alerts if a["metric"] == "response_time"]
        assert len(response_alerts) > 0


class TestAPIEndpoints:
    """Тесты новых API эндпоинтов"""

    def test_metrics_endpoint(self):
        """Тест эндпоинта метрик"""
        response = client.get("/metrics")
        assert response.status_code == 200

        data = response.json()
        assert "system" in data
        assert "application" in data

    def test_alerts_endpoint(self):
        """Тест эндпоинта алертов"""
        response = client.get("/alerts")
        assert response.status_code == 200

        data = response.json()
        assert "alerts" in data
        assert "timestamp" in data

    def test_status_endpoint(self):
        """Тест эндпоинта статуса"""
        response = client.get("/status")
        assert response.status_code == 200

        data = response.json()
        assert "health" in data
        assert "metrics" in data
        assert "alerts" in data
        assert "timestamp" in data


class TestItemServiceImprovements:
    """Тесты улучшений сервиса товаров"""

    def test_item_validation_in_service(self, db: Session):
        """Тест валидации в сервисе товаров"""
        from app.catalog.schemas.item import ItemCreate
        from app.catalog.services.item_service import ItemService

        service = ItemService(db)

        # Тест создания товара с валидными данными
        item_data = ItemCreate(
            name="Test Item",
            description="Test description",
            price=100.50,
            category="Electronics",
        )

        try:
            item = service.create_item(item_data)
            assert item is not None
            assert item.name == "Test Item"
            assert item.price == 100.50
        except Exception as e:
            pytest.fail(f"Should not raise exception: {e}")

        # Тест создания товара с невалидными данными
        invalid_item_data = ItemCreate(
            name="",  # Пустое название
            description="Test description",
            price=-10.0,  # Отрицательная цена
            category="Electronics",
        )

        with pytest.raises(ValueError) as exc_info:
            service.create_item(invalid_item_data)

        assert "Validation errors" in str(exc_info.value)

    def test_item_search_and_filtering(self, db: Session):
        """Тест поиска и фильтрации товаров"""
        from app.catalog.schemas.item import ItemCreate
        from app.catalog.services.item_service import ItemService

        service = ItemService(db)

        # Создаем тестовые товары
        items_data = [
            ItemCreate(
                name="Laptop",
                description="Gaming laptop",
                price=1500.0,
                category="Electronics",
            ),
            ItemCreate(
                name="Phone",
                description="Smartphone",
                price=800.0,
                category="Electronics",
            ),
            ItemCreate(
                name="Book",
                description="Programming book",
                price=50.0,
                category="Books",
            ),
        ]

        for item_data in items_data:
            service.create_item(item_data)

        # Тест поиска
        search_results = service.search_items("laptop")
        assert len(search_results) > 0
        assert any("Laptop" in item.name for item in search_results)

        # Тест фильтрации по категории
        electronics = service.get_items_by_category("Electronics")
        assert len(electronics) >= 2

        # Тест фильтрации по цене
        expensive_items = service.get_items(min_price=1000.0)
        assert len(expensive_items) >= 1
        assert all(item.price >= 1000.0 for item in expensive_items)

    def test_item_categories(self, db: Session):
        """Тест получения категорий"""
        from app.catalog.schemas.item import ItemCreate
        from app.catalog.services.item_service import ItemService

        service = ItemService(db)

        # Создаем товары разных категорий
        items_data = [
            ItemCreate(
                name="Item1",
                description="Test",
                price=100.0,
                category="Electronics",
            ),
            ItemCreate(
                name="Item2", description="Test", price=100.0, category="Books"
            ),
            ItemCreate(
                name="Item3",
                description="Test",
                price=100.0,
                category="Electronics",
            ),
        ]

        for item_data in items_data:
            service.create_item(item_data)

        # Получаем категории
        categories = service.get_categories()
        assert "Electronics" in categories
        assert "Books" in categories
        assert len(categories) >= 2


if __name__ == "__main__":
    pytest.main([__file__])
