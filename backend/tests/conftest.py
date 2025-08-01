"""
Конфигурация pytest для MIG Catalog API
"""

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv


def load_test_env():
    """Загружает переменные окружения для тестов"""
    # Путь к файлу .env
    env_path = Path(__file__).parent.parent / ".env"

    if env_path.exists():
        # Загружаем переменные из .env
        load_dotenv(env_path)

        # Устанавливаем тестовые значения для критических переменных
        os.environ.setdefault("ENVIRONMENT", "testing")
        os.environ.setdefault("DEBUG", "True")

        # Отключаем кэширование и rate limiting для тестов
        os.environ.setdefault("CACHE_ENABLED", "False")
        os.environ.setdefault("RATE_LIMIT_ENABLED", "False")
        os.environ.setdefault("METRICS_ENABLED", "False")

        # Настройки логирования для тестов
        os.environ.setdefault("LOG_LEVEL", "DEBUG")

        print("✅ Тестовое окружение загружено из .env")


# Загружаем окружение при импорте модуля
load_test_env()


@pytest.fixture(scope="session")
def test_environment():
    """Фикстура для тестового окружения"""
    return {
        "environment": "testing",
        "debug": True,
        "database_url": os.getenv("DATABASE_URL"),
        "secret_key": os.getenv("SECRET_KEY"),
        "cache_enabled": False,
        "rate_limit_enabled": False,
    }


@pytest.fixture(scope="function")
def mock_db():
    """Фикстура для мока базы данных"""
    from unittest.mock import Mock

    from sqlalchemy.orm import Session

    return Mock(spec=Session)


@pytest.fixture(scope="function")
def db():
    """Фикстура для тестовой базы данных"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from app.db.base import Base

    # Используем SQLite для тестов
    engine = create_engine(
        "sqlite:///test.db", connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )

    # Создаем таблицы
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Удаляем тестовую базу данных
        import os

        if os.path.exists("test.db"):
            os.remove("test.db")


@pytest.fixture(scope="function")
def redis_client():
    """Фикстура для тестового Redis"""
    from unittest.mock import Mock

    import redis

    # Создаем мок Redis клиента
    mock_redis = Mock(spec=redis.Redis)

    # Настраиваем базовые методы
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = 1
    mock_redis.exists.return_value = False
    mock_redis.keys.return_value = []

    return mock_redis


@pytest.fixture(scope="function")
def test_user_data():
    """Фикстура с тестовыми данными пользователя"""
    return {
        "uuid": "test-user-uuid",
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "password_hash": "hashed_test_password",
    }


@pytest.fixture(scope="function")
def test_item_data():
    """Фикстура с тестовыми данными товара"""
    return {
        "uuid": "test-item-uuid",
        "name": "Test Item",
        "description": "Test description",
        "price": "100.00",
        "category": "test-category",
        "stock": 10,
    }


@pytest.fixture(scope="function")
def test_order_data():
    """Фикстура с тестовыми данными заказа"""
    return {
        "uuid": "test-order-uuid",
        "user_uuid": "test-user-uuid",
        "total_amount": "150.00",
        "status": "pending",
    }
