from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.auth import AuthService, get_current_active_user
from app.core.schemas import Token, LoginRequest, RegisterRequest
from app.users.models.user import User
from app.users.schemas.user import UserResponse

router  =  APIRouter(tags = ["authentication"])


@router.post("/login", response_model = Token)
async def login(
    login_data: LoginRequest,
    db: Session  =  Depends(get_db)
):
    """Вход в систему"""
    auth_service  =  AuthService(db)
    user  =  auth_service.authenticate_user(login_data.email, login_data.password)

    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Неверный email или пароль",
            headers = {"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Пользователь неактивен"
        )

    access_token  =  auth_service.create_access_token(data = {"sub": user.uuid})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model = UserResponse, status_code = status.HTTP_201_CREATED)
async def register(
    register_data: RegisterRequest,
    db: Session  =  Depends(get_db)
):
    """Регистрация нового пользователя"""
    from app.users.schemas.user import UserCreate

    # Создаем объект UserCreate
    user_create  =  UserCreate(
        email = register_data.email,
        username = register_data.username,
        password = register_data.password
    )

    try:
        user_service  =  AuthService(db).user_service
        user  =  user_service.create_user(user_create)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = str(e)
        )


@router.get("/me", response_model = UserResponse)
async def get_current_user_info(
    current_user: User  =  Depends(get_current_active_user)
):
    """Получить информацию о текущем пользователе"""
    return current_user


@router.post("/logout")
async def logout():
    """Выход из системы (на клиенте нужно удалить токен)"""
    return {"message": "Успешный выход из системы"}
