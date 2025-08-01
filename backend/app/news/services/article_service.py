from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.news.models.article import Article
from app.news.schemas.article import ArticleCreate, ArticleUpdate


class ArticleService:
    def __init__(self, db: Session):
        self.db = db

    def get_articles(
        self, skip: int = 0, limit: int = 100, published_only: bool = True
    ) -> List[Article]:
        """Получить список статей"""
        query = self.db.query(Article)

        if published_only:
            query = query.filter(Article.is_published)

        return query.offset(skip).limit(limit).all()

    def get_article(self, article_uuid: str) -> Optional[Article]:
        """Получить статью по UUID"""
        return (
            self.db.query(Article).filter(Article.uuid == article_uuid).first()
        )

    def create_article(self, article: ArticleCreate) -> Article:
        """Создать новую статью"""
        db_article = Article(**article.dict())

        try:
            self.db.add(db_article)
            self.db.commit()
            self.db.refresh(db_article)
            return db_article
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Ошибка при создании статьи")

    def update_article(
        self, article_uuid: str, article_update: ArticleUpdate
    ) -> Optional[Article]:
        """Обновить статью"""
        db_article = self.get_article(article_uuid)
        if not db_article:
            return None

        update_data = article_update.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_article, field, value)

        try:
            self.db.commit()
            self.db.refresh(db_article)
            return db_article
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Ошибка при обновлении статьи")

    def delete_article(self, article_uuid: str) -> bool:
        """Удалить статью"""
        db_article = self.get_article(article_uuid)
        if not db_article:
            return False

        self.db.delete(db_article)
        self.db.commit()
        return True

    def search_articles(
        self, search_term: str, skip: int = 0, limit: int = 100
    ) -> List[Article]:
        """Поиск статей по заголовку или содержанию"""
        return (
            self.db.query(Article)
            .filter(
                (Article.title.ilike(f"%{search_term}%"))
                | (Article.content.ilike(f"%{search_term}%"))
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
