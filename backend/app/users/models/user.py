from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
import uuid


class User(Base):
    """Модель пользователя"""
    __tablename__  =  "users"

    uuid  =  Column(String(36), primary_key = True, default = lambda: str(uuid.uuid4()), index = True)
    email  =  Column(String(255), unique = True, index = True, nullable = False)
    username  =  Column(String(100), unique = True, index = True, nullable = False)
    password_hash  =  Column(String(255), nullable = False)
    is_active  =  Column(Boolean, default = True)
    created_at  =  Column(DateTime(timezone = True), server_default = func.now())
    updated_at  =  Column(DateTime(timezone = True), onupdate = func.now())

    # Отношения
    orders  =  relationship("Order", back_populates = "user")

    def __repr__(self):
        return f"<User(uuid = {self.uuid}, email = '{self.email}', username = '{self.username}')>"
