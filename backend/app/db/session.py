import logging
import os
import time

from dotenv import load_dotenv
from sqlalchemy import create_engine, event, text
from sqlalchemy.exc import DisconnectionError, OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool

load_dotenv()

# Создаем логгер прямо здесь, чтобы избежать циклических импортов
logger = logging.getLogger("database")

# Получаем URL базы данных из переменных окружения
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost/mig_catalog"
)

# Настройки пула соединений
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "30"))
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))

# Создаем движок SQLAlchemy с улучшенными настройками
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_recycle=POOL_RECYCLE,
    pool_timeout=POOL_TIMEOUT,
    pool_pre_ping=True,  # Проверка соединений перед использованием
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем базовый класс для моделей
Base = declarative_base()


def get_db():
    """Генератор для получения сессии базы данных с retry логикой"""
    db = SessionLocal()
    max_retries = 3
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            # Проверяем соединение
            db.execute(text("SELECT 1"))
            yield db
            break
        except (OperationalError, DisconnectionError) as e:
            logger.warning(
                f"Database connection attempt {attempt + 1} failed: {e}"
            )
            db.close()

            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Экспоненциальная задержка
                db = SessionLocal()
            else:
                logger.error("All database connection attempts failed")
                raise
        except Exception as e:
            logger.error(f"Unexpected database error: {e}")
            raise
        finally:
            db.close()


def health_check_db() -> bool:
    """Проверка здоровья базы данных"""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


def get_db_stats() -> dict:
    """Получение статистики пула соединений"""
    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "invalid": pool.invalid(),
    }


# Event listeners для мониторинга
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Настройка SQLite (если используется)"""
    if "sqlite" in DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.close()


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Логирование checkout соединений"""
    logger.debug(
        f"Database connection checked out. Pool size: {engine.pool.size()}"
    )


@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """Логирование checkin соединений"""
    logger.debug(
        f"Database connection checked in. Pool size: {engine.pool.size()}"
    )


# Функция для закрытия всех соединений (для graceful shutdown)
def close_db_connections():
    """Закрытие всех соединений с базой данных"""
    logger.info("Closing all database connections...")
    engine.dispose()
    logger.info("Database connections closed")
