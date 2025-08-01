from sqlalchemy import Column, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.base import Base
import uuid


class Article(Base):
    """Модель статьи"""
    __tablename__  =  "articles"

    uuid  =  Column(String(36), primary_key = True, default = lambda: str(uuid.uuid4()), index = True)
    title  =  Column(String(255), nullable = False, index = True)
    content  =  Column(Text, nullable = False)
    author  =  Column(String(100), nullable = False)
    is_published  =  Column(Boolean, default = False)
    created_at  =  Column(DateTime(timezone = True), server_default = func.now())
    updated_at  =  Column(DateTime(timezone = True), onupdate = func.now())

    def __repr__(self):
        return f"<Article(uuid = {self.uuid}, title = '{self.title}', author = '{self.author}')>"
