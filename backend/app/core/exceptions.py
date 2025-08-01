from fastapi import HTTPException, status
from typing import Optional, Dict, Any
from sqlalchemy.exc import OperationalError, IntegrityError, DataError, ProgrammingError


class CustomHTTPException(HTTPException):
    """Кастомное исключение с дополнительными полями"""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str]  =  None,
        headers: Optional[Dict[str, str]]  =  None
    ):
        super().__init__(status_code = status_code, detail = detail, headers = headers)
        self.error_code  =  error_code


class ItemNotFoundException(CustomHTTPException):
    def __init__(self, item_id: Optional[str]  =  None):
        detail  =  "Товар не найден"
        if item_id:
            detail  =  f"Товар с ID {item_id} не найден"
        super().__init__(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = detail,
            error_code = "ITEM_NOT_FOUND"
        )


class UserNotFoundException(CustomHTTPException):
    def __init__(self, user_id: Optional[str]  =  None):
        detail  =  "Пользователь не найден"
        if user_id:
            detail  =  f"Пользователь с ID {user_id} не найден"
        super().__init__(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = detail,
            error_code = "USER_NOT_FOUND"
        )


class OrderNotFoundException(CustomHTTPException):
    def __init__(self, order_id: Optional[str]  =  None):
        detail  =  "Заказ не найден"
        if order_id:
            detail  =  f"Заказ с ID {order_id} не найден"
        super().__init__(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = detail,
            error_code = "ORDER_NOT_FOUND"
        )


class ArticleNotFoundException(CustomHTTPException):
    def __init__(self, article_id: Optional[str]  =  None):
        detail  =  "Статья не найдена"
        if article_id:
            detail  =  f"Статья с ID {article_id} не найдена"
        super().__init__(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = detail,
            error_code = "ARTICLE_NOT_FOUND"
        )


class DuplicateUserException(CustomHTTPException):
    def __init__(self, field: str  =  "email или username"):
        super().__init__(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"Пользователь с таким {field} уже существует",
            error_code = "DUPLICATE_USER"
        )


class InvalidCredentialsException(CustomHTTPException):
    def __init__(self):
        super().__init__(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Неверный email или пароль",
            error_code = "INVALID_CREDENTIALS",
            headers = {"WWW-Authenticate": "Bearer"},
        )


class InactiveUserException(CustomHTTPException):
    def __init__(self):
        super().__init__(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Пользователь неактивен",
            error_code = "INACTIVE_USER"
        )


class ValidationErrorException(CustomHTTPException):
    def __init__(self, field: str, message: str):
        super().__init__(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"Ошибка валидации поля '{field}': {message}",
            error_code = "VALIDATION_ERROR"
        )


class RateLimitExceededException(CustomHTTPException):
    def __init__(self, retry_after: int  =  60):
        super().__init__(
            status_code = status.HTTP_429_TOO_MANY_REQUESTS,
            detail = f"Слишком много запросов. Попробуйте через {retry_after} секунд.",
            error_code = "RATE_LIMIT_EXCEEDED",
            headers = {"Retry-After": str(retry_after)}
        )


class DatabaseConnectionException(CustomHTTPException):
    def __init__(self, original_error: Optional[Exception]  =  None):
        detail  =  "Ошибка подключения к базе данных"
        if original_error:
            detail += f": {str(original_error)}"
        super().__init__(
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE,
            detail = detail,
            error_code = "DATABASE_CONNECTION_ERROR"
        )


class DatabaseQueryException(CustomHTTPException):
    def __init__(self, operation: str, original_error: Exception):
        detail  =  f"Ошибка выполнения запроса {operation}"
        if isinstance(original_error, IntegrityError):
            detail += ": нарушение целостности данных"
        elif isinstance(original_error, DataError):
            detail += ": ошибка данных"
        elif isinstance(original_error, ProgrammingError):
            detail += ": ошибка SQL"

        super().__init__(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = detail,
            error_code = "DATABASE_QUERY_ERROR"
        )


class DatabaseTimeoutException(CustomHTTPException):
    def __init__(self, operation: str):
        super().__init__(
            status_code = status.HTTP_504_GATEWAY_TIMEOUT,
            detail = f"Таймаут выполнения операции {operation}",
            error_code = "DATABASE_TIMEOUT"
        )


class InternalServerException(CustomHTTPException):
    def __init__(self, message: str  =  "Внутренняя ошибка сервера"):
        super().__init__(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = message,
            error_code = "INTERNAL_SERVER_ERROR"
        )


class PermissionDeniedException(CustomHTTPException):
    def __init__(self, resource: str  =  "ресурс"):
        super().__init__(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = f"Доступ к {resource} запрещен",
            error_code = "PERMISSION_DENIED"
        )


class ResourceConflictException(CustomHTTPException):
    def __init__(self, resource: str, conflict_reason: str):
        super().__init__(
            status_code = status.HTTP_409_CONFLICT,
            detail = f"Конфликт {resource}: {conflict_reason}",
            error_code = "RESOURCE_CONFLICT"
        )


class ServiceUnavailableException(CustomHTTPException):
    def __init__(self, service: str, retry_after: int  =  30):
        super().__init__(
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE,
            detail = f"Сервис {service} временно недоступен",
            error_code = "SERVICE_UNAVAILABLE",
            headers = {"Retry-After": str(retry_after)}
        )


def handle_database_error(operation: str, error: Exception) -> CustomHTTPException:
    """Обработчик ошибок базы данных с детализацией"""
    if isinstance(error, OperationalError):
        return DatabaseConnectionException(error)
    elif isinstance(error, IntegrityError):
        return DatabaseQueryException(operation, error)
    elif isinstance(error, DataError):
        return DatabaseQueryException(operation, error)
    elif isinstance(error, ProgrammingError):
        return DatabaseQueryException(operation, error)
    else:
        return InternalServerException(f"Неожиданная ошибка БД: {str(error)}")


def create_retry_exception(operation: str, attempt: int, max_attempts: int) -> CustomHTTPException:
    """Создает исключение для retry логики"""
    return ServiceUnavailableException(
        f"{operation} (попытка {attempt}/{max_attempts})",
        retry_after = 2 ** attempt  # Экспоненциальная задержка
    )
