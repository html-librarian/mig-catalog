from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    username: str

    @validator('username')
    def validate_username(cls, v):
        import re
        if len(v) < 3 or len(v) > 20:
            raise ValueError("Имя пользователя должно содержать 3-20 символов")

        # Проверяем на недопустимые символы
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError("Имя пользователя может содержать только буквы, цифры и подчеркивания")

        # Проверяем на зарезервированные имена
        reserved_names  =  {
            'admin', 'root', 'system', 'user', 'test', 'guest',
            'anonymous', 'null', 'undefined', 'api', 'www'
        }

        if v.lower() in reserved_names:
            raise ValueError("Имя пользователя зарезервировано")

        # Проверяем на последовательные подчеркивания
        if '__' in v:
            raise ValueError("Имя пользователя не может содержать двойные подчеркивания")

        return v


class UserCreate(UserBase):
    password: str  =  Field(..., min_length = 8, description = "Пароль (минимум 8 символов)")

    @validator('password')
    def validate_password(cls, v):
        import re
        if len(v) < 8:
            raise ValueError("Пароль должен содержать минимум 8 символов")
        if len(v) > 128:
            raise ValueError("Пароль не должен превышать 128 символов")
        if not re.search(r'[a-zA-Z]', v):
            raise ValueError("Пароль должен содержать хотя бы одну букву")
        if not re.search(r'\d', v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Пароль должен содержать хотя бы один специальный символ")
        # Проверяем на простые пароли
        common_passwords  =  ['password', '123456', 'qwerty', 'admin', 'user']
        if v.lower() in common_passwords:
            raise ValueError("Пароль слишком простой")
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr]  =  None
    username: Optional[str]  =  None
    password: Optional[str]  =  None
    is_active: Optional[bool]  =  None


class UserResponse(UserBase):
    uuid: str  =  Field(..., description = "UUID пользователя")
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]  =  None

    class Config:
        from_attributes  =  True
