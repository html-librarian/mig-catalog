import os
import threading
import time
from typing import Dict, Optional, Tuple

import redis
from dotenv import load_dotenv
from fastapi import HTTPException, status

from app.core.logging import get_logger

load_dotenv()

logger = get_logger("rate_limiter")


class RateLimiter:
    """Улучшенный Rate limiter для защиты от DDoS атак"""

    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.memory_store: Dict[str, Tuple[int, float]] = {}
        self.memory_lock = threading.Lock()
        self.cleanup_interval = 300  # 5 минут
        self.last_cleanup = time.time()

        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
            )
            # Проверяем подключение
            self.redis_client.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}, using memory store")
            self.redis_client = None

    def _get_key(self, identifier: str, endpoint: str) -> str:
        """Генерирует ключ для rate limiting"""
        return f"rate_limit:{identifier}:{endpoint}"

    def _cleanup_memory_store(self):
        """Очистка старых записей из памяти"""
        current_time = time.time()
        if current_time - self.last_cleanup < self.cleanup_interval:
            return

        with self.memory_lock:
            keys_to_remove = []
            for key, (count, timestamp) in self.memory_store.items():
                if current_time - timestamp > 3600:  # 1 час
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del self.memory_store[key]

            self.last_cleanup = current_time
            if keys_to_remove:
                logger.debug(
                    f"Cleaned up {len(keys_to_remove)} old rate limit entries"
                )

    def _get_memory_data(self, key: str) -> Tuple[int, float]:
        """Получает данные из памяти с очисткой"""
        self._cleanup_memory_store()

        with self.memory_lock:
            if key in self.memory_store:
                count, timestamp = self.memory_store[key]
                # Очищаем старые записи (старше 1 минуты)
                if time.time() - timestamp > 60:
                    del self.memory_store[key]
                    return 0, time.time()
                return count, timestamp
            return 0, time.time()

    def _set_memory_data(self, key: str, count: int, timestamp: float):
        """Устанавливает данные в памяти"""
        with self.memory_lock:
            self.memory_store[key] = (count, timestamp)

    def _get_rate_limits(self, endpoint: str) -> Tuple[int, int]:
        """Получает лимиты для конкретного эндпоинта"""
        # Дифференцированные лимиты для разных эндпоинтов
        limits = {
            "/api/v1/auth/login": (5, 60),  # 5 попыток входа в минуту
            "/api/v1/auth/register": (3, 300),  # 3 регистрации в 5 минут
            "/api/v1/users/": (100, 60),  # 100 запросов в минуту
            "/api/v1/items/": (200, 60),  # 200 запросов в минуту
            "/api/v1/orders/": (50, 60),  # 50 запросов в минуту
            "/api/v1/news/": (100, 60),  # 100 запросов в минуту
        }

        # Ищем точное совпадение или используем дефолт
        for pattern, (max_req, window) in limits.items():
            if endpoint.startswith(pattern):
                return max_req, window

        # Дефолтные лимиты
        return 100, 60

    def check_rate_limit(
        self,
        identifier: str,
        endpoint: str,
        max_requests: Optional[int] = None,
        window_seconds: Optional[int] = None,
    ):
        """Проверяет rate limit для идентификатора и эндпоинта"""
        # Отключаем rate limiting для тестов
        if os.getenv("TESTING", "false").lower() == "true":
            return True

        # Получаем лимиты для эндпоинта
        if max_requests is None or window_seconds is None:
            max_requests, window_seconds = self._get_rate_limits(endpoint)

        key = self._get_key(identifier, endpoint)
        current_time = time.time()

        if self.redis_client:
            # Используем Redis
            try:
                # Получаем текущий счетчик
                current_count = self.redis_client.get(key)
                if current_count is None:
                    # Первый запрос
                    self.redis_client.setex(key, window_seconds, 1)
                    return True

                count = int(current_count)
                if count >= max_requests:
                    logger.warning(
                        f"Rate limit exceeded for {identifier} on {endpoint}: "
                        f"{count}/{max_requests}"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=(
                            f"Слишком много запросов. "
                            f"Попробуйте через {window_seconds} секунд."
                        ),
                        headers={"Retry-After": str(window_seconds)},
                    )

                # Увеличиваем счетчик
                self.redis_client.incr(key)
                return True

            except HTTPException:
                raise
            except Exception as e:
                # Если Redis недоступен, переключаемся на память
                logger.warning(f"Redis error: {e}, switching to memory")
                self.redis_client = None

        # Используем память
        count, timestamp = self._get_memory_data(key)

        # Проверяем, не истекло ли время окна
        if current_time - timestamp > window_seconds:
            # Сбрасываем счетчик
            self._set_memory_data(key, 1, current_time)
            return True

        # Проверяем лимит
        if count >= max_requests:
            logger.warning(
                f"Rate limit exceeded for {identifier} on {endpoint}: "
                f"{count}/{max_requests}"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"Слишком много запросов. "
                    f"Попробуйте через {window_seconds} секунд."
                ),
                headers={"Retry-After": str(window_seconds)},
            )

        # Увеличиваем счетчик
        self._set_memory_data(key, count + 1, timestamp)
        return True

    def get_rate_limit_info(self, identifier: str, endpoint: str) -> dict:
        """Получает информацию о текущих лимитах"""
        key = self._get_key(identifier, endpoint)
        max_requests, window_seconds = self._get_rate_limits(endpoint)

        if self.redis_client:
            try:
                current_count = self.redis_client.get(key)
                count = int(current_count) if current_count else 0
                ttl = self.redis_client.ttl(key)
            except Exception:
                count, timestamp = self._get_memory_data(key)
                ttl = max(0, window_seconds - (time.time() - timestamp))
        else:
            count, timestamp = self._get_memory_data(key)
            ttl = max(0, window_seconds - (time.time() - timestamp))

        return {
            "current_requests": count,
            "max_requests": max_requests,
            "window_seconds": window_seconds,
            "remaining_requests": max(0, max_requests - count),
            "reset_in_seconds": ttl,
        }


# Глобальный экземпляр rate limiter
rate_limiter = RateLimiter()
