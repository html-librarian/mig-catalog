import time
import uuid
import json
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import get_logger
from app.core.rate_limiter import rate_limiter
from app.core.security import security_manager

logger = get_logger("middleware")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Улучшенный middleware для логирования запросов"""

    def __init__(self, app):
        super().__init__(app)
        self.sensitive_headers = {'authorization', 'cookie', 'x-api-key'}
        self.sensitive_paths = {'/api/v1/auth/login', '/api/v1/auth/register'}

    def _mask_sensitive_data(self, data: dict) -> dict:
        """Маскирует чувствительные данные"""
        masked = data.copy()
        sensitive_fields = {'password', 'token', 'secret', 'key'}

        for field in sensitive_fields:
            if field in masked:
                masked[field] = '***MASKED***'

        return masked

    def _get_client_ip(self, request: Request) -> str:
        """Получает реальный IP адрес клиента"""
        # Проверяем заголовки прокси
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()

        real_ip = request.headers.get('x-real-ip')
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"

    def _should_log_request_body(self, path: str) -> bool:
        """Определяет, нужно ли логировать тело запроса"""
        return path in self.sensitive_paths

    async def dispatch(self, request: Request, call_next):
        # Генерируем correlation ID
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id

        start_time = time.time()
        client_ip = self._get_client_ip(request)

        # Проверяем, не заблокирован ли IP
        if security_manager.is_ip_blacklisted(client_ip):
            logger.warning(f"Blocked request from blacklisted IP: {client_ip}")
            return Response(
                status_code=429,
                content=json.dumps({
                    "detail": "IP заблокирован из-за множественных неудачных попыток",
                    "correlation_id": correlation_id
                }),
                media_type="application/json"
            )

        # Логируем входящий запрос
        log_data = {
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": client_ip,
            "user_agent": request.headers.get("user-agent", ""),
            "timestamp": time.time()
        }

        # Добавляем заголовки (исключая чувствительные)
        headers = dict(request.headers)
        for header in self.sensitive_headers:
            if header in headers:
                headers[header] = "***MASKED***"
        log_data["headers"] = headers

        # Логируем тело запроса для чувствительных эндпоинтов
        if self._should_log_request_body(request.url.path):
            try:
                body = await request.body()
                if body:
                    body_str = body.decode('utf-8')
                    try:
                        body_json = json.loads(body_str)
                        masked_body = self._mask_sensitive_data(body_json)
                        log_data["request_body"] = masked_body
                    except json.JSONDecodeError:
                        log_data["request_body"] = "***NON_JSON_BODY***"
            except Exception as e:
                log_data["request_body_error"] = str(e)

        logger.info(f"Request started: {json.dumps(log_data, ensure_ascii=False)}")

        try:
            # Проверяем rate limit для всех запросов
            try:
                rate_limiter.check_rate_limit(
                    identifier=client_ip,
                    endpoint=request.url.path
                )
            except Exception as rate_limit_error:
                # Записываем неудачную попытку
                security_manager.record_failed_attempt(client_ip, request.url.path)
                
                rate_limit_data = {
                    'correlation_id': correlation_id,
                    'client_ip': client_ip,
                    'path': request.url.path,
                    'error': str(rate_limit_error)
                }
                logger.warning(
                    f"Rate limit exceeded: {json.dumps(rate_limit_data, ensure_ascii=False)}"
                )
                raise rate_limit_error

            response = await call_next(request)

            # Логируем успешный ответ
            process_time = time.time() - start_time
            response_log = {
                "correlation_id": correlation_id,
                "status_code": response.status_code,
                "process_time": round(process_time, 3),
                "content_length": response.headers.get("content-length", 0)
            }

            logger.info(f"Request completed: {json.dumps(response_log, ensure_ascii=False)}")

            # Добавляем correlation ID в заголовки ответа
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Process-Time"] = str(round(process_time, 3))

            return response

        except Exception as e:
            # Логируем ошибку
            process_time = time.time() - start_time
            error_log = {
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
                "client_ip": client_ip,
                "process_time": round(process_time, 3),
                "error_type": type(e).__name__,
                "error_message": str(e)
            }

            logger.error(f"Request failed: {json.dumps(error_log, ensure_ascii=False)}")
            raise


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Улучшенный middleware для обработки ошибок"""

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Получаем correlation ID
            correlation_id = getattr(request.state, 'correlation_id', 'unknown')

            # Логируем ошибку без чувствительной информации
            error_data = {
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
                "error_type": type(e).__name__,
                "error_message": str(e)
            }

            logger.error(f"Unhandled error: {json.dumps(error_data, ensure_ascii=False)}")

            # Возвращаем стандартную ошибку 500 без раскрытия деталей
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Внутренняя ошибка сервера",
                    "error_code": "INTERNAL_SERVER_ERROR",
                    "correlation_id": correlation_id
                },
                headers={"X-Correlation-ID": correlation_id}
            )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware для добавления заголовков безопасности"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Добавляем заголовки безопасности
        security_headers = security_manager.get_security_headers()
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response
