from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import os
import secrets
from dotenv import load_dotenv

from app.db.session import get_db
from app.users.models.user import User
from app.users.services.user_service import UserService

load_dotenv()

# Настройки безопасности
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Критическая проверка SECRET_KEY во всех окружениях
if not SECRET_KEY:
    raise ValueError("SECRET_KEY must be set in all environments!")
elif len(SECRET_KEY) < 64:  # Увеличиваем минимальную длину
    raise ValueError("SECRET_KEY must be at least 64 characters long!")
elif (SECRET_KEY == "your-secret-key-here" or  # nosec
      "default" in SECRET_KEY.lower() or
      "your-super-secret" in SECRET_KEY.lower()):
    raise ValueError("SECRET_KEY must be changed from default value!")

# Генерация дополнительного ключа для ротации
ROTATION_SECRET_KEY = os.getenv("ROTATION_SECRET_KEY")
if not ROTATION_SECRET_KEY:
    ROTATION_SECRET_KEY = secrets.token_urlsafe(64)  # Увеличиваем длину

# Настройка хеширования паролей с улучшенными параметрами
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=14  # Увеличиваем количество раундов для большей безопасности
)

# Настройка HTTP Bearer
security = HTTPBearer()

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверить пароль"""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Хешировать пароль"""
        return pwd_context.hash(password)

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Аутентификация пользователя с защитой от timing attacks"""
        user = self.user_service.get_user_by_email(email)
        if not user:
            # Используем постоянное время для предотвращения timing attacks
            pwd_context.verify("dummy_password", pwd_context.hash("dummy"))
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        return user

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Создать JWT токен с улучшенной безопасностью"""
        to_encode = data.copy()
        current_time = datetime.utcnow()
        
        if expires_delta:
            expire = current_time + expires_delta
        else:
            expire = current_time + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        # Добавляем дополнительные claims для безопасности
        to_encode.update({
            "exp": expire,
            "iat": current_time,  # Время создания токена
            "nbf": current_time,  # Not Before - токен недействителен до этого времени
            "iss": "mig-catalog-api",
            "aud": "mig-catalog-users",
            "jti": secrets.token_urlsafe(32),  # Уникальный ID токена
            "type": "access"
        })

        # Используем основной ключ для новых токенов
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[dict]:
        """Проверить JWT токен с улучшенной валидацией"""
        try:
            # Сначала пробуем основной ключ
            payload = jwt.decode(
                token, 
                SECRET_KEY, 
                algorithms=[ALGORITHM],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_nbf": True,
                    "require": ["exp", "iat", "nbf", "iss", "aud", "jti", "type"]
                }
            )
            
            # Дополнительные проверки
            if payload.get("iss") != "mig-catalog-api":
                return None
            if payload.get("aud") != "mig-catalog-users":
                return None
            if payload.get("type") != "access":
                return None
                
            return payload
        except JWTError:
            try:
                # Если не получилось, пробуем ключ ротации
                payload = jwt.decode(
                    token, 
                    ROTATION_SECRET_KEY, 
                    algorithms=[ALGORITHM],
                    options={
                        "verify_signature": True,
                        "verify_exp": True,
                        "verify_iat": True,
                        "verify_nbf": True,
                        "require": ["exp", "iat", "nbf", "iss", "aud", "jti", "type"]
                    }
                )
                
                # Дополнительные проверки
                if payload.get("iss") != "mig-catalog-api":
                    return None
                if payload.get("aud") != "mig-catalog-users":
                    return None
                if payload.get("type") != "access":
                    return None
                    
                return payload
            except JWTError:
                return None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Получить текущего пользователя из токена с улучшенной безопасностью"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Пробуем оба ключа для поддержки ротации
        payload = None
        try:
            payload = jwt.decode(
                credentials.credentials, 
                SECRET_KEY, 
                algorithms=[ALGORITHM],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_nbf": True,
                    "require": ["exp", "iat", "nbf", "iss", "aud", "jti", "type", "sub"]
                }
            )
        except JWTError:
            payload = jwt.decode(
                credentials.credentials, 
                ROTATION_SECRET_KEY, 
                algorithms=[ALGORITHM],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_nbf": True,
                    "require": ["exp", "iat", "nbf", "iss", "aud", "jti", "type", "sub"]
                }
            )

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

    user_service = UserService(db)
    user = user_service.get_user(user_uuid)
    if user is None:
        raise credentials_exception

    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Получить текущего активного пользователя"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Неактивный пользователь")
    return current_user

def create_token_for_user(user: User) -> str:
    """Создать токен для пользователя"""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return AuthService(None).create_access_token(
        data={"sub": user.uuid}, expires_delta=access_token_expires
    )
