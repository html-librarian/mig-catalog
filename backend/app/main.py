import os
import time

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.catalog import items_router
from app.core.auth_api import router as auth_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import (
    ErrorHandlingMiddleware,
    LoggingMiddleware,
    PerformanceMonitoringMiddleware,
    RateLimitingMiddleware,
    RequestValidationMiddleware,
    SecurityHeadersMiddleware,
)
from app.core.monitoring import (
    check_alerts,
    get_health_status,
    get_system_metrics,
)
from app.db.base_class import Base
from app.db.session import engine
from app.news import articles_router
from app.orders import orders_router
from app.users import users_router

# Загружаем переменные окружения
load_dotenv()

# Настраиваем логирование
logger = setup_logging()

# В продакшене используем миграции вместо create_all
if os.getenv("ENVIRONMENT") != "production":
    # Только для разработки - создаем таблицы автоматически
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        if os.getenv("ENVIRONMENT") == "production":
            raise
        else:
            logger.warning(
                "Continuing in development mode despite database error"
            )
else:
    # В продакшене таблицы должны быть созданы через миграции
    logger.info(
        "Production environment detected. Tables should be created via migrations."
    )

# Создаем экземпляр FastAPI
app = FastAPI(
    title="MIG Catalog API",
    description="""
    # MIG Catalog API

    REST API для электронной коммерции с полным циклом управления товарами, пользователями и заказами.

    ## Основные модули

    * **Auth** - JWT аутентификация и авторизация
    * **Users** - Управление пользователями и профилями
    * **Items** - Каталог товаров с категориями
    * **Orders** - Система заказов и их обработка
    * **News** - Контент-менеджмент для статей

    ## Авторизация

    ```
    Authorization: Bearer <jwt-token>
    ```

    ## Технологический стек

    FastAPI • PostgreSQL • Redis • SQLAlchemy • JWT
    """,
    version="1.4.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "MIG Development Team",
        "email": "dev@mig-catalog.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Добавляем middleware в правильном порядке
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(PerformanceMonitoringMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestValidationMiddleware)
app.add_middleware(RateLimitingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создаем основной роутер для API v1

api_v1_router = APIRouter(prefix="/api/v1")

# Подключаем роутеры к API v1
api_v1_router.include_router(auth_router, prefix="/auth")
api_v1_router.include_router(users_router, prefix="/users")
api_v1_router.include_router(items_router, prefix="/items")
api_v1_router.include_router(orders_router, prefix="/orders")
api_v1_router.include_router(articles_router, prefix="/news")

# Подключаем основной API роутер
app.include_router(api_v1_router)


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Добро пожаловать в MIG Catalog API",
        "version": "1.4.0",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
    }


@app.get("/health")
async def health_check():
    """Базовая проверка состояния API"""
    return {
        "status": "healthy",
        "service": "mig-catalog-api",
        "version": "1.4.0",
    }


@app.get("/health/detailed")
async def detailed_health_check():
    """Детальная проверка состояния всех сервисов"""
    return get_health_status()


@app.get("/metrics")
async def get_metrics():
    """Метрики производительности"""
    return get_system_metrics()


@app.get("/alerts")
async def get_alerts():
    """Получить активные алерты"""
    return {"alerts": check_alerts(), "timestamp": time.time()}


@app.get("/status")
async def get_status():
    """Полный статус системы"""
    return {
        "health": get_health_status(),
        "metrics": get_system_metrics(),
        "alerts": check_alerts(),
        "timestamp": time.time(),
    }
