from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.users.models.user import User
from app.users.schemas.user import UserCreate, UserUpdate
from passlib.context import CryptContext

# Настройка хеширования паролей
pwd_context  =  CryptContext(schemes = ["bcrypt"], deprecated = "auto")


class UserService:
    def __init__(self, db: Session):
        self.db  =  db

    def get_users(self, skip: int  =  0, limit: int  =  100) -> List[User]:
        """Получить список пользователей"""
        return self.db.query(User).offset(skip).limit(limit).all()

    def get_user(self, user_id: str) -> Optional[User]:
        """Получить пользователя по UUID"""
        return self.db.query(User).filter(User.uuid == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        return self.db.query(User).filter(User.email == email).first()

    def create_user(self, user: UserCreate) -> User:
        """Создать нового пользователя"""
        # Проверяем, не существует ли уже пользователь с таким email
        existing_user  =  self.get_user_by_email(user.email)
        if existing_user:
            raise ValueError(f"Пользователь с email '{user.email}' уже существует")

        # Проверяем, не существует ли уже пользователь с таким username
        existing_username  =  self.db.query(User).filter(User.username == user.username).first()
        if existing_username:
            raise ValueError(f"Пользователь с username '{user.username}' уже существует")

        # Хешируем пароль
        hashed_password  =  pwd_context.hash(user.password)

        db_user  =  User(
            email = user.email,
            username = user.username,
            password_hash = hashed_password
        )

        try:
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Ошибка создания пользователя: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Неожиданная ошибка при создании пользователя: {str(e)}")

    def update_user(self, user_id: str, user_update: UserUpdate) -> Optional[User]:
        """Обновить пользователя"""
        db_user  =  self.get_user(user_id)
        if not db_user:
            return None

        update_data  =  user_update.dict(exclude_unset = True)

        # Проверяем уникальность email, если он обновляется
        if "email" in update_data:
            existing_user  =  self.get_user_by_email(update_data["email"])
            if existing_user and existing_user.uuid != user_id:
                raise ValueError(f"Пользователь с email '{update_data['email']}' уже существует")

        # Проверяем уникальность username, если он обновляется
        if "username" in update_data:
            existing_username  =  self.db.query(User).filter(
                User.username == update_data["username"],
                User.uuid != user_id
            ).first()
            if existing_username:
                raise ValueError(f"Пользователь с username '{update_data['username']}' уже существует")

        # Если обновляется пароль, хешируем его
        if "password" in update_data:
            update_data["password_hash"]  =  pwd_context.hash(update_data.pop("password"))

        for field, value in update_data.items():
            setattr(db_user, field, value)

        try:
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Ошибка обновления пользователя: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Неожиданная ошибка при обновлении пользователя: {str(e)}")

    def delete_user(self, user_id: str) -> bool:
        """Удалить пользователя"""
        db_user  =  self.get_user(user_id)
        if not db_user:
            return False

        self.db.delete(db_user)
        self.db.commit()
        return True

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверить пароль"""
        return pwd_context.verify(plain_password, hashed_password)
