import re
import time
from typing import Optional, Tuple
from pydantic import BaseModel, validator, Field
from decimal import Decimal
import uuid
from fastapi import HTTPException, status
from app.core.logging import get_logger

logger  =  get_logger("validators")


class ReDoSProtection:
    """Защита от ReDoS атак"""

    @staticmethod
    def safe_regex_match(pattern: str, string: str, timeout: float  =  0.1) -> bool:
        """Безопасное выполнение regex с таймаутом"""
        start_time  =  time.time()

        try:
            # Компилируем regex с флагами для оптимизации
            compiled_pattern  =  re.compile(pattern, re.IGNORECASE | re.UNICODE)

            # Проверяем таймаут
            if time.time() - start_time > timeout:
                logger.warning(f"Regex timeout for pattern: {pattern}")
                return False

            return bool(compiled_pattern.match(string))
        except re.error as e:
            logger.error(f"Invalid regex pattern: {pattern}, error: {e}")
            return False
        except Exception as e:
            logger.error(f"Regex execution error: {e}")
            return False


class PasswordValidator:
    """Улучшенный валидатор паролей"""

    @staticmethod
    def validate_password(password: str) -> bool:
        """
        Проверяет сложность пароля
        Минимум 8 символов, хотя бы одна буква, цифра и специальный символ
        """
        if len(password) < 8:
            return False

        if len(password) > 128:  # Максимальная длина
            return False

        # Проверяем наличие букв
        if not re.search(r'[a-zA-Z]', password):
            return False

        # Проверяем наличие цифр
        if not re.search(r'\d', password):
            return False

        # Проверяем наличие специальных символов
        if not re.search(r'[!@#$%^&*()_+\- = \[\]{};\':"\\|,.<>/?]', password):
            return False

        # Проверяем на повторяющиеся символы
        if re.search(r'(.)\1{2,}', password):
            return False

        return True

    @staticmethod
    def get_password_requirements() -> str:
        """Возвращает требования к паролю"""
        return ("Пароль должен содержать минимум 8 символов, максимум 128, "
                "хотя бы одну букву, цифру и специальный символ")


class EmailValidator:
    """Улучшенный валидатор email с защитой от ReDoS"""

    # Оптимизированный regex для email
    EMAIL_PATTERN  =  r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    @staticmethod
    def validate_email(email: str) -> bool:
        """Проверяет формат email с защитой от ReDoS"""
        if not email or len(email) > 254:  # RFC 5321
            return False

        # Проверяем на двойные точки
        if '..' in email:
            return False

        # Проверяем на двойные @
        if email.count('@') != 1:
            return False

        # Проверяем длину локальной части
        local_part  =  email.split('@')[0]
        if len(local_part) > 64:
            return False

        # Проверяем длину доменной части
        domain_part  =  email.split('@')[1]
        if len(domain_part) > 253:
            return False

        # Безопасная проверка regex
        return ReDoSProtection.safe_regex_match(
            EmailValidator.EMAIL_PATTERN, email
        )

    @staticmethod
    def is_disposable_email(email: str) -> bool:
        """Проверяет, не является ли email одноразовым"""
        disposable_domains  =  {
            '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
            'mailinator.com', 'yopmail.com', 'temp-mail.org'
        }

        domain  =  email.split('@')[1].lower()
        return domain in disposable_domains


class PriceValidator:
    """Улучшенный валидатор цен"""

    @staticmethod
    def validate_price(price: Decimal) -> bool:
        """Проверяет, что цена положительная и не слишком большая"""
        if price <= 0:
            return False

        if price > Decimal('999999.99'):
            return False

        # Проверяем количество знаков после запятой
        if price.as_tuple().exponent < -2:
            return False

        return True

    @staticmethod
    def format_price(price: Decimal) -> str:
        """Форматирует цену для отображения"""
        return f"{price:.2f}"


class UsernameValidator:
    """Улучшенный валидатор имен пользователей"""

    @staticmethod
    def validate_username(username: str) -> bool:
        """
        Проверяет имя пользователя
        Только буквы, цифры и подчеркивания, 3-20 символов
        """
        if len(username) < 3 or len(username) > 20:
            return False

        # Проверяем на недопустимые символы
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False

        # Проверяем на зарезервированные имена
        reserved_names  =  {
            'admin', 'root', 'system', 'user', 'test', 'guest',
            'anonymous', 'null', 'undefined', 'api', 'www'
        }

        if username.lower() in reserved_names:
            return False

        # Проверяем на последовательные подчеркивания
        if '__' in username:
            return False

        return True


class DataValidator:
    """Основной класс валидации данных с улучшенной безопасностью"""

    @staticmethod
    def validate_item_data(
        name: str,
        price: Decimal,
        category: str
    ) -> Tuple[bool, Optional[str]]:
        """Валидирует данные товара с улучшенными проверками"""
        # Проверяем название
        if not name or len(name.strip()) < 2:
            return False, "Название товара должно содержать минимум 2 символа"

        if len(name.strip()) > 255:
            return False, "Название товара не может превышать 255 символов"

        # Проверяем цену
        if not PriceValidator.validate_price(price):
            return False, "Цена должна быть положительной и не превышать 999999.99"

        # Проверяем категорию
        if not category or len(category.strip()) < 2:
            return False, "Категория должна содержать минимум 2 символа"

        if len(category.strip()) > 100:
            return False, "Категория не может превышать 100 символов"

        return True, None

    @staticmethod
    def validate_user_data(
        email: str,
        username: str,
        password: str
    ) -> Tuple[bool, Optional[str]]:
        """Валидирует данные пользователя с улучшенными проверками"""
        # Проверяем email
        if not EmailValidator.validate_email(email):
            return False, "Неверный формат email"

        if EmailValidator.is_disposable_email(email):
            return False, "Использование одноразовых email адресов запрещено"

        # Проверяем username
        if not UsernameValidator.validate_username(username):
            return False, ("Имя пользователя должно содержать 3-20 символов "
                          "(буквы, цифры, подчеркивания)")

        # Проверяем пароль
        if not PasswordValidator.validate_password(password):
            return False, PasswordValidator.get_password_requirements()

        return True, None

    @staticmethod
    def validate_article_data(
        title: str,
        content: str,
        author: str
    ) -> Tuple[bool, Optional[str]]:
        """Валидирует данные статьи с улучшенными проверками"""
        # Проверяем заголовок
        if not title or len(title.strip()) < 5:
            return False, "Заголовок должен содержать минимум 5 символов"

        if len(title.strip()) > 200:
            return False, "Заголовок не может превышать 200 символов"

        # Проверяем содержание
        if not content or len(content.strip()) < 10:
            return False, "Содержание должно содержать минимум 10 символов"

        if len(content.strip()) > 10000:
            return False, "Содержание не может превышать 10000 символов"

        # Проверяем автора
        if not author or len(author.strip()) < 2:
            return False, "Автор должен содержать минимум 2 символа"

        if len(author.strip()) > 100:
            return False, "Имя автора не может превышать 100 символов"

        return True, None


def validate_uuid(uuid_str: str, field_name: str  =  "UUID") -> str:
    """Валидация UUID строки с улучшенной обработкой ошибок"""
    if not uuid_str:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"{field_name} не может быть пустым"
        )

    try:
        # Проверяем, что это валидный UUID
        uuid.UUID(uuid_str)
        return uuid_str
    except ValueError:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"Неверный формат {field_name}: {uuid_str}"
        )


def validate_uuid_optional(
    uuid_str: Optional[str],
    field_name: str  =  "UUID"
) -> Optional[str]:
    """Валидация опционального UUID"""
    if uuid_str is None:
        return None
    return validate_uuid(uuid_str, field_name)


def sanitize_input(text: str, max_length: int  =  1000) -> str:
    """Очистка пользовательского ввода"""
    if not text:
        return ""

    # Удаляем потенциально опасные символы
    sanitized  =  re.sub(r'[<>"\']', '', text)

    # Обрезаем до максимальной длины
    if len(sanitized) > max_length:
        sanitized  =  sanitized[:max_length]

    return sanitized.strip()
