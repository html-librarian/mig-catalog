"""
Модуль кэширования с Redis
"""

import hashlib
import json
from functools import wraps
from typing import Any, Callable, Optional

import redis

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("cache")


class CacheManager:
    """Менеджер кэширования с Redis"""

    def __init__(self):
        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
        )
        self.default_ttl = settings.CACHE_TTL
        self.enabled = settings.CACHE_ENABLED

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Генерирует ключ кэша на основе аргументов"""
        key_parts = [prefix]

        # Добавляем аргументы
        if args:
            key_parts.extend([str(arg) for arg in args])

        # Добавляем именованные аргументы
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            key_parts.extend([f"{k}:{v}" for k, v in sorted_kwargs])

        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Получить значение из кэша"""
        if not self.enabled:
            return None

        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Установить значение в кэш"""
        if not self.enabled:
            return False

        try:
            ttl = ttl or self.default_ttl
            serialized_value = json.dumps(value, default=str)
            return self.redis_client.setex(key, ttl, serialized_value)
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Удалить значение из кэша"""
        if not self.enabled:
            return False

        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """Удалить все ключи по паттерну"""
        if not self.enabled:
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error: {e}")
            return 0

    def exists(self, key: str) -> bool:
        """Проверить существование ключа"""
        if not self.enabled:
            return False

        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False

    def get_stats(self) -> dict:
        """Получить статистику кэша"""
        if not self.enabled:
            return {"enabled": False}

        try:
            info = self.redis_client.info()
            return {
                "enabled": True,
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "total_keys": info.get("db0", {}).get("keys", 0),
                "hit_rate": info.get("keyspace_hits", 0)
                / max(info.get("keyspace_misses", 1), 1),
            }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {"enabled": False, "error": str(e)}


# Глобальный экземпляр менеджера кэша
cache_manager = CacheManager()


def cached(prefix: str, ttl: Optional[int] = None):
    """
    Алиас для декоратора cache для обратной совместимости
    """
    return cache(prefix, ttl)


def cache(
    prefix: str,
    ttl: Optional[int] = None,
    key_generator: Optional[Callable] = None,
):
    """
    Декоратор для кэширования результатов функций

    Args:
        prefix: Префикс для ключей кэша
        ttl: Время жизни кэша в секундах
        key_generator: Функция для генерации ключа кэша
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not cache_manager.enabled:
                return await func(*args, **kwargs)

            # Генерируем ключ кэша
            if key_generator:
                cache_key = key_generator(prefix, *args, **kwargs)
            else:
                cache_key = cache_manager._generate_key(
                    prefix, *args, **kwargs
                )

            # Пытаемся получить из кэша
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_result

            # Выполняем функцию и кэшируем результат
            result = await func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            logger.debug(f"Cache miss for key: {cache_key}, cached result")

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not cache_manager.enabled:
                return func(*args, **kwargs)

            # Генерируем ключ кэша
            if key_generator:
                cache_key = key_generator(prefix, *args, **kwargs)
            else:
                cache_key = cache_manager._generate_key(
                    prefix, *args, **kwargs
                )

            # Пытаемся получить из кэша
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_result

            # Выполняем функцию и кэшируем результат
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            logger.debug(f"Cache miss for key: {cache_key}, cached result")

            return result

        # Возвращаем асинхронную или синхронную обертку
        if (
            func.__name__.startswith("async_")
            or hasattr(func, "__code__")
            and func.__code__.co_flags & 0x80
        ):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def invalidate_cache(prefix: str):
    """
    Декоратор для инвалидации кэша после выполнения функции

    Args:
        prefix: Префикс ключей для удаления
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            cache_manager.delete_pattern(f"{prefix}:*")
            logger.debug(f"Invalidated cache for prefix: {prefix}")
            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            cache_manager.delete_pattern(f"{prefix}:*")
            logger.debug(f"Invalidated cache for prefix: {prefix}")
            return result

        # Возвращаем асинхронную или синхронную обертку
        if (
            func.__name__.startswith("async_")
            or hasattr(func, "__code__")
            and func.__code__.co_flags & 0x80
        ):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
