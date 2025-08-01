from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from typing import List
from pydantic import Field
from app.db.session import get_db
from app.users.models.user import User
from app.users.schemas.user import UserCreate, UserUpdate, UserResponse
from app.users.services.user_service import UserService
from app.core.validators import validate_uuid
from app.core.auth import get_current_user

router  =  APIRouter(tags = ["users"])


@router.get("/", response_model = List[UserResponse])
async def get_users(
    skip: int  =  0,
    limit: int  =  100,
    db: Session  =  Depends(get_db)
):
    """
    Получить список всех пользователей

    Возвращает пагинированный список пользователей системы.

    **Параметры:**
    - `skip`: Количество записей для пропуска (для пагинации)
    - `limit`: Максимальное количество записей для возврата

    **Возвращает:**
    - Список пользователей с их основными данными

    **Пример ответа:**
    ```json
    [
        {
            "uuid": "550e8400-e29b-41d4-a716-446655440000",
            "email": "user@example.com",
            "username": "testuser",
            "is_active": true,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    ]
    ```
    """
    users  =  UserService(db).get_users(skip = skip, limit = limit)
    return users


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Получить информацию о текущем пользователе"""
    return current_user


@router.get("/{user_id}", response_model = UserResponse)
async def get_user(
    user_id: str  =  Path(..., description = "UUID пользователя"),
    db: Session  =  Depends(get_db)
):
    """Получить пользователя по UUID"""
    # Валидируем UUID
    validate_uuid(user_id, "UUID пользователя")

    user  =  UserService(db).get_user(user_id)
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Пользователь не найден"
        )
    return user


@router.post("/", response_model = UserResponse, status_code = status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session  =  Depends(get_db)):
    """Создать нового пользователя"""
    return UserService(db).create_user(user)


@router.put("/{user_id}", response_model = UserResponse)
async def update_user(
    user_update: UserUpdate,
    user_id: str  =  Path(..., description = "UUID пользователя"),
    db: Session  =  Depends(get_db)
):
    """Обновить пользователя по UUID"""
    # Валидируем UUID
    validate_uuid(user_id, "UUID пользователя")

    user  =  UserService(db).update_user(user_id, user_update)
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Пользователь не найден"
        )
    return user


@router.delete("/{user_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str  =  Path(..., description = "UUID пользователя"),
    db: Session  =  Depends(get_db)
):
    """Удалить пользователя по UUID"""
    # Валидируем UUID
    validate_uuid(user_id, "UUID пользователя")

    success  =  UserService(db).delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Пользователь не найден"
        )
