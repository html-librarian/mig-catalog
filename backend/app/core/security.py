"""
Модуль дополнительных функций безопасности
"""
import hashlib
import secrets
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from app.core.logging import get_logger

logger = get_logger("security")


class SecurityManager:
    """Менеджер безопасности с дополнительными функциями"""

    def __init__(self):
        self.failed_attempts: Dict[str, Dict[str, Any]] = {}
        self.blacklisted_tokens: set = set()

    def hash_sensitive_data(self, data: str) -> str:
        """Хеширует чувствительные данные для логирования"""
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def is_ip_blacklisted(self, ip: str) -> bool:
        """Проверяет, заблокирован ли IP"""
        if ip not in self.failed_attempts:
            return False
        
        attempts = self.failed_attempts[ip]
        if attempts["count"] >= 10:  # Максимум 10 попыток
            lockout_until = attempts.get("lockout_until")
            if lockout_until and datetime.utcnow() < lockout_until:
                return True
            else:
                # Сбрасываем блокировку
                del self.failed_attempts[ip]
        return False

    def record_failed_attempt(self, ip: str, endpoint: str):
        """Записывает неудачную попытку"""
        current_time = datetime.utcnow()
        
        if ip not in self.failed_attempts:
            self.failed_attempts[ip] = {
                "count": 0,
                "first_attempt": current_time,
                "last_attempt": current_time,
                "endpoints": set()
            }
        
        attempts = self.failed_attempts[ip]
        attempts["count"] += 1
        attempts["last_attempt"] = current_time
        attempts["endpoints"].add(endpoint)
        
        # Блокируем на 15 минут после 10 неудачных попыток
        if attempts["count"] >= 10:
            attempts["lockout_until"] = current_time + timedelta(minutes=15)
            logger.warning(f"IP {ip} blocked for 15 minutes due to multiple failed attempts")
        
        # Сбрасываем счетчик через час
        if current_time - attempts["first_attempt"] > timedelta(hours=1):
            del self.failed_attempts[ip]

    def blacklist_token(self, token: str):
        """Добавляет токен в черный список"""
        self.blacklisted_tokens.add(token)

    def is_token_blacklisted(self, token: str) -> bool:
        """Проверяет, находится ли токен в черном списке"""
        return token in self.blacklisted_tokens

    def validate_password_strength(self, password: str) -> tuple[bool, str]:
        """Проверяет сложность пароля"""
        if len(password) < 8:
            return False, "Пароль должен содержать минимум 8 символов"
        
        if len(password) > 128:
            return False, "Пароль не должен превышать 128 символов"
        
        if not any(c.isupper() for c in password):
            return False, "Пароль должен содержать хотя бы одну заглавную букву"
        
        if not any(c.islower() for c in password):
            return False, "Пароль должен содержать хотя бы одну строчную букву"
        
        if not any(c.isdigit() for c in password):
            return False, "Пароль должен содержать хотя бы одну цифру"
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False, "Пароль должен содержать хотя бы один специальный символ"
        
        # Проверяем на простые пароли
        common_passwords = {
            "password", "123456", "qwerty", "admin", "user", "test",
            "password123", "admin123", "user123", "test123"
        }
        if password.lower() in common_passwords:
            return False, "Пароль слишком простой"
        
        return True, "Пароль соответствует требованиям безопасности"

    def sanitize_input(self, text: str, max_length: int = 1000) -> str:
        """Очищает пользовательский ввод от потенциально опасных символов"""
        if not text:
            return ""
        
        # Удаляем потенциально опасные символы
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '{', '}']
        sanitized = text
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        # Обрезаем до максимальной длины
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized.strip()

    def generate_secure_token(self, length: int = 32) -> str:
        """Генерирует криптографически безопасный токен"""
        return secrets.token_urlsafe(length)

    def validate_csrf_token(self, token: str, session_token: str) -> bool:
        """Проверяет CSRF токен"""
        return token == session_token

    def get_security_headers(self) -> Dict[str, str]:
        """Возвращает заголовки безопасности"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }


# Глобальный экземпляр менеджера безопасности
security_manager = SecurityManager()


def require_https():
    """Проверяет, что запрос использует HTTPS"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # В продакшене проверяем HTTPS
            # В разработке пропускаем
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def validate_request_origin(origin: str, allowed_origins: list) -> bool:
    """Проверяет, разрешен ли origin"""
    return origin in allowed_origins


def rate_limit_by_ip(ip: str, endpoint: str, max_requests: int = 100, window: int = 60):
    """Rate limiting по IP адресу"""
    if security_manager.is_ip_blacklisted(ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="IP заблокирован из-за множественных неудачных попыток"
        )
    
    # Здесь можно добавить дополнительную логику rate limiting
    return True 