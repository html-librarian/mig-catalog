from typing import List, Optional

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

from dotenv import load_dotenv
from pydantic import field_validator

load_dotenv()


class Settings(BaseSettings):
    """Настройки приложения с валидацией"""

    # Основные настройки
    APP_NAME: str = "MIG Catalog API"
    APP_VERSION: str = "1.3.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # База данных
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost/mig_catalog"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 30
    DB_POOL_RECYCLE: int = 3600
    DB_POOL_TIMEOUT: int = 30

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Безопасность
    SECRET_KEY: str
    ROTATION_SECRET_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080"

    # Логирование
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: int = 100
    RATE_LIMIT_WINDOW: int = 60

    # Кэширование
    CACHE_TTL: int = 3600
    CACHE_ENABLED: bool = True

    # Мониторинг
    METRICS_ENABLED: bool = True
    HEALTH_CHECK_ENABLED: bool = True

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v):
        if not v:
            raise ValueError("SECRET_KEY must be set")
        if len(v) < 64:  # Увеличиваем минимальную длину
            raise ValueError("SECRET_KEY must be at least 64 characters long")
        default_patterns = ["default", "your-secret", "your-super-secret"]
        if any(pattern in v.lower() for pattern in default_patterns):
            raise ValueError("SECRET_KEY must be changed from default value")
        return v

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v):
        if not v:
            raise ValueError("DATABASE_URL must be set")
        if not v.startswith(("postgresql://", "postgres://")):
            raise ValueError("DATABASE_URL must be a valid PostgreSQL URL")
        return v

    @field_validator("REDIS_URL")
    @classmethod
    def validate_redis_url(cls, v):
        if not v:
            raise ValueError("REDIS_URL must be set")
        if not v.startswith("redis://"):
            raise ValueError("REDIS_URL must be a valid Redis URL")
        return v

    @property
    def allowed_origins_list(self) -> List[str]:
        """Получить список разрешенных origins"""
        if not self.ALLOWED_ORIGINS:
            return ["http://localhost:3000", "http://localhost:8080"]
        return [
            origin.strip()
            for origin in self.ALLOWED_ORIGINS.split(",")
            if origin.strip()
        ]

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v):
        allowed = ["development", "staging", "production", "testing"]
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v):
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}")
        return v.upper()

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Игнорировать дополнительные поля


# Создаем экземпляр настроек
settings = Settings()


def get_settings() -> Settings:
    """Получить настройки приложения"""
    return settings


def validate_production_settings():
    """Проверка настроек для продакшена"""
    if settings.ENVIRONMENT == "production":
        # Дополнительные проверки для продакшена
        if settings.DEBUG:
            raise ValueError("DEBUG must be False in production")

        if not settings.SECRET_KEY or len(settings.SECRET_KEY) < 64:
            raise ValueError(
                "SECRET_KEY must be at least 64 characters in production"
            )

        if "localhost" in settings.DATABASE_URL:
            raise ValueError(
                "DATABASE_URL must not contain localhost in production"
            )

        if "localhost" in settings.REDIS_URL:
            raise ValueError(
                "REDIS_URL must not contain localhost in production"
            )

        if "*" in settings.allowed_origins_list:
            raise ValueError(
                "ALLOWED_ORIGINS must not contain wildcards in production"
            )

        # Проверяем, что ROTATION_SECRET_KEY установлен в продакшене
        if not settings.ROTATION_SECRET_KEY:
            raise ValueError("ROTATION_SECRET_KEY must be set in production")


# Проверяем настройки при импорте
validate_production_settings()
