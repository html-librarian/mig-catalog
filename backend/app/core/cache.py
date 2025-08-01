import json
import time
import hashlib
from typing import Any, Optional, Union
import redis
import os
from functools import wraps
from app.core.logging import get_logger

logger  =  get_logger("cache")


class CacheManager:
    """Менеджер кэширования с поддержкой Redis и fallback на память"""

    def __init__(self):
        self.redis_url  =  os.getenv("REDIS_URL", "redis://localhost:6379")
        self.memory_cache  =  {}
        self.memory_ttl  =  {}

        try:
            self.redis_client  =  redis.from_url(
                self.redis_url,
                decode_responses = True,
                socket_connect_timeout = 5,
                socket_timeout = 5,
                retry_on_timeout = True
            )
            self.redis_client.ping()
            self.use_redis  =  True
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"Redis cache failed: {e}, using memory cache")
            self.redis_client  =  None
            self.use_redis  =  False

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Генерирует ключ кэша на основе аргументов"""
        key_parts  =  [prefix]

        # Добавляем позиционные аргументы
        for arg in args:
            key_parts.append(str(arg))

        # Добавляем именованные аргументы
        for key, value in sorted(kwargs.items()):
            key_parts.append(f"{key}:{value}")

        key_string  =  ":".join(key_parts)
        return hashlib.md5(key_string.encode(), usedforsecurity=False).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Получает значение из кэша"""
        if self.use_redis:
            try:
                value  =  self.redis_client.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                logger.warning(f"Redis get error: {e}")
                self.use_redis  =  False

        # Fallback на память
        if key in self.memory_cache:
            # Проверяем TTL
            if key in self.memory_ttl:
                if time.time() > self.memory_ttl[key]:
                    del self.memory_cache[key]
                    del self.memory_ttl[key]
                    return None
            return self.memory_cache[key]

        return None

    def set(self, key: str, value: Any, ttl: int  =  3600) -> bool:
        """Устанавливает значение в кэш"""
        try:
            serialized_value  =  json.dumps(value, ensure_ascii = False)

            if self.use_redis:
                try:
                    self.redis_client.setex(key, ttl, serialized_value)
                    return True
                except Exception as e:
                    logger.warning(f"Redis set error: {e}")
                    self.use_redis  =  False

            # Fallback на память
            self.memory_cache[key]  =  value
            self.memory_ttl[key]  =  time.time() + ttl
            return True

        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Удаляет значение из кэша"""
        try:
            if self.use_redis:
                try:
                    self.redis_client.delete(key)
                except Exception as e:
                    logger.warning(f"Redis delete error: {e}")
                    self.use_redis  =  False

            # Удаляем из памяти
            if key in self.memory_cache:
                del self.memory_cache[key]
            if key in self.memory_ttl:
                del self.memory_ttl[key]

            return True

        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """Очищает кэш по паттерну"""
        deleted_count  =  0

        if self.use_redis:
            try:
                keys  =  self.redis_client.keys(pattern)
                if keys:
                    deleted_count  =  self.redis_client.delete(*keys)
            except Exception as e:
                logger.warning(f"Redis clear pattern error: {e}")
                self.use_redis  =  False

        # Очищаем память по паттерну
        keys_to_delete  =  []
        for key in self.memory_cache.keys():
            if pattern.replace('*', '') in key:
                keys_to_delete.append(key)

        for key in keys_to_delete:
            del self.memory_cache[key]
            if key in self.memory_ttl:
                del self.memory_ttl[key]
            deleted_count += 1

        return deleted_count

    def get_stats(self) -> dict:
        """Получает статистику кэша"""
        stats  =  {
            "memory_items": len(self.memory_cache),
            "memory_ttl_items": len(self.memory_ttl),
            "use_redis": self.use_redis
        }

        if self.use_redis:
            try:
                stats["redis_info"]  =  self.redis_client.info()
            except Exception as e:
                stats["redis_error"]  =  str(e)

        return stats


# Глобальный экземпляр кэша
cache_manager  =  CacheManager()


def cached(prefix: str, ttl: int  =  3600):
    """Декоратор для кэширования результатов функций"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Генерируем ключ кэша
            cache_key  =  cache_manager._generate_key(prefix, *args, **kwargs)

            # Пытаемся получить из кэша
            cached_result  =  cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result

            # Выполняем функцию
            result  =  func(*args, **kwargs)

            # Сохраняем в кэш
            cache_manager.set(cache_key, result, ttl)
            logger.debug(f"Cache miss for {func.__name__}, stored result")

            return result
        return wrapper
    return decorator


def invalidate_cache(prefix: str):
    """Декоратор для инвалидации кэша"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Выполняем функцию
            result  =  func(*args, **kwargs)

            # Инвалидируем кэш
            pattern  =  f"{prefix}:*"
            deleted_count  =  cache_manager.clear_pattern(pattern)
            logger.debug(f"Invalidated {deleted_count} cache entries for {func.__name__}")

            return result
        return wrapper
    return decorator


class CacheKeys:
    """Константы для ключей кэша"""
    USER_PROFILE  =  "user:profile"
    ITEM_DETAILS  =  "item:details"
    ITEM_LIST  =  "item:list"
    ORDER_DETAILS  =  "order:details"
    ARTICLE_DETAILS  =  "article:details"
    ARTICLE_LIST  =  "article:list"
    RATE_LIMIT  =  "rate_limit"
    HEALTH_CHECK  =  "health:check"
