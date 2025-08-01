"""
Модуль валидации данных
"""

import re
import unicodedata
from typing import List, Optional, Tuple

from email_validator import EmailNotValidError, validate_email

from app.core.logging import get_logger

logger = get_logger("validators")


class PasswordValidator:
    """Валидатор паролей с улучшенными проверками"""

    MIN_LENGTH = 8
    MAX_LENGTH = 128

    @staticmethod
    def validate_password(password: str) -> Tuple[bool, List[str]]:
        """
        Валидация пароля

        Returns:
            Tuple[bool, List[str]]: (валидный, список ошибок)
        """
        errors = []

        if not password:
            errors.append("Пароль не может быть пустым")
            return False, errors

        # Проверка длины
        if len(password) < PasswordValidator.MIN_LENGTH:
            errors.append(
                f"Пароль должен содержать минимум "
                f"{PasswordValidator.MIN_LENGTH} символов"
            )

        if len(password) > PasswordValidator.MAX_LENGTH:
            errors.append(
                f"Пароль не должен превышать "
                f"{PasswordValidator.MAX_LENGTH} символов"
            )

        # Проверка символов
        if not any(c.isupper() for c in password):
            errors.append(
                "Пароль должен содержать хотя бы одну заглавную букву"
            )

        if not any(c.islower() for c in password):
            errors.append(
                "Пароль должен содержать хотя бы одну строчную букву"
            )

        if not any(c.isdigit() for c in password):
            errors.append("Пароль должен содержать хотя бы одну цифру")

        # Проверка специальных символов
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            errors.append(
                "Пароль должен содержать хотя бы один специальный символ"
            )

        # Проверка на простые пароли
        if PasswordValidator._is_common_password(password):
            errors.append("Пароль слишком простой")

        # Проверка на повторяющиеся символы
        if PasswordValidator._has_repeating_chars(password):
            errors.append("Пароль не должен содержать повторяющиеся символы")

        # Проверка на последовательности
        if PasswordValidator._has_sequences(password):
            errors.append(
                "Пароль не должен содержать последовательности символов"
            )

        return len(errors) == 0, errors

    @staticmethod
    def _is_common_password(password: str) -> bool:
        """Проверка на простые пароли"""
        common_passwords = {
            "password",
            "123456",
            "qwerty",
            "admin",
            "user",
            "test",
            "password123",
            "admin123",
            "user123",
            "test123",
            "12345678",
            "qwerty123",
            "letmein",
            "welcome",
            "monkey",
            "dragon",
        }
        return password.lower() in common_passwords

    @staticmethod
    def _has_repeating_chars(password: str) -> bool:
        """Проверка на повторяющиеся символы"""
        for i in range(len(password) - 2):
            if password[i] == password[i + 1] == password[i + 2]:
                return True
        return False

    @staticmethod
    def _has_sequences(password: str) -> bool:
        """Проверка на последовательности символов"""
        # Проверяем только очевидные последовательности
        sequences = ["123456", "abcdef", "qwerty", "asdfgh", "zxcvbn"]
        password_lower = password.lower()
        for seq in sequences:
            if seq in password_lower:
                return True
        return False

    @staticmethod
    def get_password_requirements() -> str:
        """Получить требования к паролю"""
        return (
            f"Пароль должен содержать минимум "
            f"{PasswordValidator.MIN_LENGTH} символов, "
            "хотя бы одну заглавную букву, строчную букву, "
            "цифру и специальный символ"
        )


class EmailValidator:
    """Валидатор email адресов"""

    DISPOSABLE_DOMAINS = {
        "10minutemail.com",
        "tempmail.org",
        "guerrillamail.com",
        "mailinator.com",
        "yopmail.com",
        "temp-mail.org",
        "sharklasers.com",
        "grr.la",
        "guerrillamailblock.com",
    }

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, List[str]]:
        """
        Валидация email адреса

        Returns:
            Tuple[bool, List[str]]: (валидный, список ошибок)
        """
        errors = []

        if not email:
            errors.append("Email не может быть пустым")
            return False, errors

        # Проверка длины
        if len(email) > 254:  # RFC 5321
            errors.append("Email не может превышать 254 символа")
            return False, errors

        # Проверка формата (без проверки реальных доменов)
        try:
            validated_email = validate_email(email, check_deliverability=False)
            email = validated_email.email
        except EmailNotValidError as e:
            errors.append(f"Неверный формат email: {str(e)}")
            return False, errors

        # Проверка на одноразовые домены
        if EmailValidator.is_disposable_email(email):
            errors.append("Использование одноразовых email адресов запрещено")

        # Дополнительные проверки
        if EmailValidator._has_suspicious_patterns(email):
            errors.append("Email содержит подозрительные символы")

        return len(errors) == 0, errors

    @staticmethod
    def is_disposable_email(email: str) -> bool:
        """Проверка на одноразовый email"""
        domain = email.split("@")[-1].lower()
        return domain in EmailValidator.DISPOSABLE_DOMAINS

    @staticmethod
    def _has_suspicious_patterns(email: str) -> bool:
        """Проверка на подозрительные паттерны"""
        suspicious_patterns = [
            r"\.{2,}",  # Двойные точки
            r'[<>"\']',  # HTML теги
            r"javascript:",  # JavaScript
            r"data:",  # Data URI
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, email, re.IGNORECASE):
                return True
        return False


class UsernameValidator:
    """Валидатор имен пользователей"""

    MIN_LENGTH = 3
    MAX_LENGTH = 20
    RESERVED_NAMES = {
        "admin",
        "root",
        "system",
        "user",
        "test",
        "guest",
        "anonymous",
        "null",
        "undefined",
        "api",
        "www",
        "mail",
        "ftp",
        "localhost",
        "support",
        "info",
        "help",
    }

    @staticmethod
    def validate_username(username: str) -> Tuple[bool, List[str]]:
        """
        Валидация имени пользователя

        Returns:
            Tuple[bool, List[str]]: (валидный, список ошибок)
        """
        errors = []

        if not username:
            errors.append("Имя пользователя не может быть пустым")
            return False, errors

        # Проверка длины
        if len(username) < UsernameValidator.MIN_LENGTH:
            errors.append(
                f"Имя пользователя должно содержать минимум "
                f"{UsernameValidator.MIN_LENGTH} символа"
            )

        if len(username) > UsernameValidator.MAX_LENGTH:
            errors.append(
                f"Имя пользователя не должно превышать "
                f"{UsernameValidator.MAX_LENGTH} символов"
            )

        # Проверка символов
        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            errors.append(
                "Имя пользователя может содержать только буквы, "
                "цифры и подчеркивание"
            )

        # Проверка на зарезервированные имена
        if username.lower() in UsernameValidator.RESERVED_NAMES:
            errors.append("Это имя пользователя зарезервировано")

        # Проверка на последовательности
        if UsernameValidator._has_sequences(username):
            errors.append(
                "Имя пользователя не должно содержать "
                "последовательности символов"
            )

        # Проверка на повторяющиеся символы
        if UsernameValidator._has_repeating_chars(username):
            errors.append(
                "Имя пользователя не должно содержать повторяющиеся символы"
            )

        return len(errors) == 0, errors

    @staticmethod
    def _has_sequences(username: str) -> bool:
        """Проверка на последовательности символов"""
        # Проверяем только очевидные последовательности
        sequences = ["123456", "abcdef", "qwerty", "asdfgh", "zxcvbn"]
        username_lower = username.lower()
        for seq in sequences:
            if seq in username_lower:
                return True
        return False

    @staticmethod
    def _has_repeating_chars(username: str) -> bool:
        """Проверка на повторяющиеся символы"""
        for i in range(len(username) - 2):
            if username[i] == username[i + 1] == username[i + 2]:
                return True
        return False


class InputSanitizer:
    """Санітизатор входных данных"""

    @staticmethod
    def sanitize_text(text: str, max_length: int = 1000) -> str:
        """
        Очистка текста от потенциально опасных символов

        Args:
            text: Исходный текст
            max_length: Максимальная длина

        Returns:
            str: Очищенный текст
        """
        if not text:
            return ""

        # Нормализация Unicode
        text = unicodedata.normalize("NFKC", text)

        # Удаление потенциально опасных символов
        dangerous_chars = ["<", ">", '"', "'", "&", ";", "(", ")", "{", "}"]
        for char in dangerous_chars:
            text = text.replace(char, "")

        # Удаление HTML тегов
        text = re.sub(r"<[^>]+>", "", text)

        # Удаление JavaScript
        text = re.sub(r"javascript:", "", text, flags=re.IGNORECASE)
        text = re.sub(r"data:", "", text, flags=re.IGNORECASE)

        # Удаление лишних пробелов
        text = re.sub(r"\s+", " ", text).strip()

        # Обрезка до максимальной длины
        if len(text) > max_length:
            text = text[:max_length]

        return text

    @staticmethod
    def sanitize_html(text: str) -> str:
        """Очистка HTML от опасных тегов"""
        if not text:
            return ""

        # Разрешенные теги
        allowed_tags = {
            "b",
            "i",
            "u",
            "em",
            "strong",
            "p",
            "br",
            "div",
            "span",
        }

        # Удаляем все теги кроме разрешенных
        pattern = r"<(?!\/?(?:" + "|".join(allowed_tags) + r")\b)[^>]+>"
        text = re.sub(pattern, "", text)

        return text


def validate_item_data(
    name: str, price: float, category: str
) -> Tuple[bool, List[str]]:
    """Валидация данных товара"""
    errors = []

    # Валидация названия
    if not name or not name.strip():
        errors.append("Название товара не может быть пустым")
    elif len(name) > 255:
        errors.append("Название товара не может превышать 255 символов")

    # Валидация цены
    if price < 0:
        errors.append("Цена не может быть отрицательной")
    elif price > 99999999.99:
        errors.append("Цена не может превышать 99,999,999.99")

    # Валидация категории
    if not category or not category.strip():
        errors.append("Категория не может быть пустой")
    elif len(category) > 100:
        errors.append("Категория не может превышать 100 символов")

    return len(errors) == 0, errors


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Санитизация входящего текста"""
    return InputSanitizer.sanitize_text(text, max_length)


def validate_uuid(uuid_value: str, field_name: str = "UUID") -> str:
    """Валидация UUID"""
    if not uuid_value:
        raise ValueError(f"{field_name} не может быть пустым")

    # Проверка формата UUID
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        re.IGNORECASE,
    )

    if not uuid_pattern.match(uuid_value):
        raise ValueError(f"{field_name} имеет неверный формат")

    return uuid_value


def validate_uuid_optional(
    uuid_value: Optional[str], field_name: str = "UUID"
) -> Optional[str]:
    """
    Валидация опционального UUID

    Args:
        uuid_value: UUID для валидации (может быть None)
        field_name: Название поля для сообщения об ошибке

    Returns:
        Optional[str]: Валидный UUID или None
    """
    if uuid_value is None:
        return None

    return validate_uuid(uuid_value, field_name)
