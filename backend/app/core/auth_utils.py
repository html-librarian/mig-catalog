import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.db.session import get_db

load_dotenv()

# Настройки безопасности
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

# Критическая проверка SECRET_KEY во всех окружениях
if not SECRET_KEY:
    # Для тестового окружения используем fallback
    if os.getenv("ENVIRONMENT") == "testing":
        SECRET_KEY = "test-secret-key-64-characters-long-for-testing-purposes-only-123456789"
    else:
        raise ValueError("SECRET_KEY must be set in all environments!")
elif len(SECRET_KEY) < 64:  # Увеличиваем минимальную длину
    if os.getenv("ENVIRONMENT") == "testing":
        SECRET_KEY = "test-secret-key-64-characters-long-for-testing-purposes-only-123456789"
    else:
        raise ValueError("SECRET_KEY must be at least 64 characters long!")
elif (
    SECRET_KEY == "your-secret-key-here"  # nosec
    or "default" in SECRET_KEY.lower()
    or "your-super-secret" in SECRET_KEY.lower()
):
    if os.getenv("ENVIRONMENT") == "testing":
        SECRET_KEY = "test-secret-key-64-characters-long-for-testing-purposes-only-123456789"
    else:
        raise ValueError("SECRET_KEY must be changed from default value!")

# Генерация дополнительного ключа для ротации
ROTATION_SECRET_KEY = os.getenv("ROTATION_SECRET_KEY")
if not ROTATION_SECRET_KEY:
    if os.getenv("ENVIRONMENT") == "testing":
        ROTATION_SECRET_KEY = (
            "test-rotation-key-64-characters-long-for-testing-purposes-only"
        )
    else:
        ROTATION_SECRET_KEY = secrets.token_urlsafe(64)  # Увеличиваем длину

# Настройка хеширования паролей с улучшенными параметрами
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=14,  # Увеличиваем количество раундов для безопасности
)

# Настройка HTTP Bearer
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверить пароль"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хешировать пароль"""
    return pwd_context.hash(password)


def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """Создать JWT токен с улучшенной безопасностью"""
    to_encode = data.copy()
    current_time = datetime.utcnow()

    if expires_delta:
        expire = current_time + expires_delta
    else:
        expire = current_time + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Добавляем дополнительные claims для безопасности
    to_encode.update(
        {
            "exp": expire,
            "iat": current_time,
            "nbf": current_time,
            "iss": "mig-catalog-api",
            "aud": "mig-catalog-users",
            "type": "access",
            "jti": secrets.token_urlsafe(32),
        }
    )

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Проверить JWT токен"""
    try:
        # Пробуем основной ключ
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "verify_nbf": True,
                "require": [
                    "exp",
                    "iat",
                    "nbf",
                    "iss",
                    "aud",
                    "jti",
                    "type",
                    "sub",
                ],
            },
        )
        return payload
    except JWTError:
        try:
            # Пробуем ключ ротации
            payload = jwt.decode(
                token,
                ROTATION_SECRET_KEY,
                algorithms=[ALGORITHM],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_nbf": True,
                    "require": [
                        "exp",
                        "iat",
                        "nbf",
                        "iss",
                        "aud",
                        "jti",
                        "type",
                        "sub",
                    ],
                },
            )
            return payload
        except JWTError:
            return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Получить текущего пользователя из JWT токена"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception

        # Дополнительные проверки безопасности
        if payload.get("iss") != "mig-catalog-api":
            raise credentials_exception
        if payload.get("aud") != "mig-catalog-users":
            raise credentials_exception
        if payload.get("type") != "access":
            raise credentials_exception

        user_uuid: str = payload.get("sub")
        if user_uuid is None:
            raise credentials_exception

        # Проверяем, не слишком ли старый токен (максимум 1 час)
        iat = payload.get("iat")
        if iat:
            token_created = datetime.fromtimestamp(iat)
            if datetime.utcnow() - token_created > timedelta(hours=1):
                raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Импортируем здесь, чтобы избежать циклических импортов
    from app.users.services.user_service import UserService

    user_service = UserService(db)
    user = user_service.get_user(user_uuid)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(current_user=Depends(get_current_user)):
    """Получить текущего активного пользователя"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Неактивный пользователь")
    return current_user


def create_token_for_user(user) -> str:
    """Создать токен для пользователя"""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_access_token(
        data={"sub": user.uuid}, expires_delta=access_token_expires
    )
