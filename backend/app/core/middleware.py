"""
Middleware для обработки запросов, логирования и безопасности
"""

import time
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger
from app.core.monitoring import record_request_metrics
from app.core.security import security_manager

logger = get_logger("middleware")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования запросов"""

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        start_time = time.time()

        # Логируем начало запроса
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client_ip": (
                    request.client.host if request.client else "unknown"
                ),
                "user_agent": request.headers.get("user-agent", "unknown"),
            },
        )

        try:
            response = await call_next(request)

            # Рассчитываем время выполнения
            process_time = time.time() - start_time

            # Логируем успешный ответ
            logger.info(
                f"Request completed: {request.method} {request.url.path} - "
                f"{response.status_code} ({process_time:.3f}s)",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time": process_time,
                    "client_ip": (
                        request.client.host if request.client else "unknown"
                    ),
                },
            )

            # Записываем метрики
            record_request_metrics(
                request.url.path,
                request.method,
                response.status_code,
                process_time,
            )

            return response

        except Exception as e:
            # Рассчитываем время выполнения
            process_time = time.time() - start_time

            # Логируем ошибку
            logger.error(
                f"Request failed: {request.method} {request.url.path} - "
                f"Error: {str(e)} ({process_time:.3f}s)",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "process_time": process_time,
                    "client_ip": (
                        request.client.host if request.client else "unknown"
                    ),
                },
            )

            # Записываем метрики ошибки
            record_request_metrics(
                request.url.path, request.method, 500, process_time
            )

            raise


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware для обработки ошибок"""

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            # Логируем необработанную ошибку
            logger.error(
                f"Unhandled exception: {str(e)}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "client_ip": (
                        request.client.host if request.client else "unknown"
                    ),
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                },
            )

            # Возвращаем стандартную ошибку
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": "Произошла внутренняя ошибка сервера",
                    "timestamp": time.time(),
                },
            )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware для добавления заголовков безопасности"""

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        response = await call_next(request)

        # Не применяем CSP для документации, чтобы ReDoc работал
        if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
            security_headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block",
                "Referrer-Policy": "strict-origin-when-cross-origin",
            }
        else:
            # Добавляем заголовки безопасности для остальных эндпоинтов
            security_headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block",
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
                "Content-Security-Policy": (
                    "default-src 'self'; script-src 'self' 'unsafe-inline' "
                    "'unsafe-eval' blob: https://cdn.jsdelivr.net; style-src "
                    "'self' 'unsafe-inline' https://cdn.jsdelivr.net "
                    "https://fonts.googleapis.com; img-src 'self' data: https: "
                    "blob:; font-src 'self' https://cdn.jsdelivr.net "
                    "https://fonts.gstatic.com; worker-src 'self' blob:;"
                ),
                "Referrer-Policy": "strict-origin-when-cross-origin",
                "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            }

        for header, value in security_headers.items():
            response.headers[header] = value

        return response


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Middleware для rate limiting"""

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        # Получаем IP клиента
        client_ip = request.client.host if request.client else "unknown"

        # Проверяем, не заблокирован ли IP
        if security_manager.is_ip_blacklisted(client_ip):
            logger.warning(f"Blocked request from blacklisted IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too many requests",
                    "message": (
                        "IP заблокирован из-за множественных "
                        "неудачных попыток"
                    ),
                },
            )

        # Проверяем rate limiting
        try:
            # Здесь можно добавить более сложную логику rate limiting
            # Пока просто пропускаем запрос
            pass
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # В случае ошибки rate limiting пропускаем запрос

        return await call_next(request)


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Middleware для валидации запросов"""

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        # Проверяем размер запроса
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB
            return JSONResponse(
                status_code=413,
                content={
                    "error": "Request too large",
                    "message": "Размер запроса превышает допустимый лимит",
                },
            )

        # Проверяем Content-Type для POST/PUT запросов
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            if not content_type.startswith(
                ("application/json", "multipart/form-data")
            ):
                return JSONResponse(
                    status_code=415,
                    content={
                        "error": "Unsupported media type",
                        "message": "Неподдерживаемый тип контента",
                    },
                )

        return await call_next(request)


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware для мониторинга производительности"""

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        start_time = time.time()

        # Добавляем заголовок для отслеживания времени
        response = await call_next(request)

        process_time = time.time() - start_time

        # Добавляем заголовок с временем обработки
        response.headers["X-Process-Time"] = str(process_time)

        # Логируем медленные запросы
        if process_time > 1.0:  # Больше 1 секунды
            logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"took {process_time:.3f}s",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "process_time": process_time,
                    "client_ip": (
                        request.client.host if request.client else "unknown"
                    ),
                },
            )

        return response
