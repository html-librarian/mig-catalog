from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.users import users_router
from app.catalog import items_router
from app.orders import orders_router
from app.news import articles_router
from app.core.auth_api import router as auth_router
from app.core.middleware import LoggingMiddleware, ErrorHandlingMiddleware, SecurityHeadersMiddleware
from app.core.logging import setup_logging
from app.db.base import Base
from app.db.session import engine, health_check_db, get_db_stats
from app.core.rate_limiter import rate_limiter
import os
from dotenv import load_dotenv
import time

# Загружаем переменные окружения
load_dotenv()

# Настраиваем логирование
logger = setup_logging()

# В продакшене используем миграции вместо create_all
if os.getenv("ENVIRONMENT") != "production":
    # Только для разработки - создаем таблицы автоматически
    Base.metadata.create_all(bind=engine)
else:
    # В продакшене таблицы должны быть созданы через миграции
    logger.info("Production environment detected. Tables should be created via migrations.")

# Создаем экземпляр FastAPI
app = FastAPI(
    title="MIG Catalog API",
    description="""
    ## MIG Catalog API

    Полнофункциональный API для каталога товаров MIG с аутентификацией и авторизацией.

    ### Основные возможности:

    * 🔐 **Аутентификация** - JWT токены, регистрация и вход
    * 👥 **Управление пользователями** - CRUD операции
    * 🛍️ **Каталог товаров** - Поиск, фильтрация, категории
    * 📦 **Система заказов** - Создание и управление заказами
    * 📰 **Новости и статьи** - Контент-менеджмент
    * 🛡️ **Безопасность** - Rate limiting, валидация данных
    * 📊 **Логирование** - Детальное логирование операций

    ### Технологии:

    * **FastAPI** - Современный веб-фреймворк
    * **SQLAlchemy** - ORM для работы с базой данных
    * **PostgreSQL** - Основная база данных
    * **Redis** - Кэширование и rate limiting
    * **JWT** - Аутентификация
    * **Pydantic** - Валидация данных

    ### Авторизация:

    Для доступа к защищенным эндпоинтам используйте Bearer токен:
    ```
    Authorization: Bearer <your-jwt-token>
    ```
    """,
    version="1.3.0",
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
app.add_middleware(LoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# Настройка CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создаем основной роутер для API v1
from fastapi import APIRouter

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
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Базовая проверка состояния API"""
    return {
        "status": "healthy",
        "service": "mig-catalog-api"
    }


@app.get("/health/detailed")
async def detailed_health_check():
    """Детальная проверка состояния всех сервисов"""
    health_status = {
        "status": "healthy",
        "service": "mig-catalog-api",
        "timestamp": time.time(),
        "checks": {}
    }

    # Проверка базы данных
    try:
        db_healthy = health_check_db()
        health_status["checks"]["database"] = {
            "status": "healthy" if db_healthy else "unhealthy",
            "details": get_db_stats() if db_healthy else None
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }

    # Проверка Redis
    try:
        redis_info = rate_limiter.get_rate_limit_info("health_check", "/health")
        health_status["checks"]["redis"] = {
            "status": "healthy",
            "details": redis_info
        }
    except Exception as e:
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }

    # Проверка переменных окружения
    required_env_vars = ["SECRET_KEY", "DATABASE_URL"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    health_status["checks"]["environment"] = {
        "status": "healthy" if not missing_vars else "unhealthy",
        "missing_variables": missing_vars if missing_vars else None
    }

    # Определяем общий статус
    all_healthy = all(
        check["status"] == "healthy"
        for check in health_status["checks"].values()
    )

    health_status["status"] = "healthy" if all_healthy else "unhealthy"

    return health_status


@app.get("/metrics")
async def get_metrics():
    """Метрики производительности"""
    import psutil

    # Системные метрики
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    # Метрики базы данных
    db_stats = get_db_stats()

    # Метрики приложения
    import gc
    gc.collect()

    return {
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available": memory.available,
            "disk_percent": disk.percent,
            "disk_free": disk.free
        },
        "database": db_stats,
        "application": {
            "gc_objects": len(gc.get_objects()),
            "gc_garbage": len(gc.garbage)
        }
    }
