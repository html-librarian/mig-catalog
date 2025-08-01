from typing import Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.catalog.services.item_service import ItemService
from app.core.auth import get_current_active_user, get_current_user
from app.db.session import get_db
from app.news.services.article_service import ArticleService
from app.orders.services.order_service import OrderService
from app.users.models.user import User
from app.users.services.user_service import UserService


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency для получения UserService"""
    return UserService(db)


def get_item_service(db: Session = Depends(get_db)) -> ItemService:
    """Dependency для получения ItemService"""
    return ItemService(db)


def get_order_service(db: Session = Depends(get_db)) -> OrderService:
    """Dependency для получения OrderService"""
    return OrderService(db)


def get_article_service(db: Session = Depends(get_db)) -> ArticleService:
    """Dependency для получения ArticleService"""
    return ArticleService(db)


def get_current_user_optional(
    current_user: Optional[User] = Depends(get_current_user),
) -> Optional[User]:
    """Dependency для получения текущего пользователя (опционально)"""
    return current_user


def require_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Dependency для проверки прав администратора"""
    if not hasattr(current_user, "is_admin") or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора",
        )
    return current_user


def require_moderator(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Dependency для проверки прав модератора"""
    if (
        not hasattr(current_user, "is_moderator")
        or not current_user.is_moderator
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права модератора",
        )
    return current_user
