from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.core.validators import validate_uuid
from app.db.session import get_db
from app.news.schemas.article import (
    ArticleCreate,
    ArticleResponse,
    ArticleUpdate,
)
from app.news.services.article_service import ArticleService

router = APIRouter(tags=["news"])


@router.get("/", response_model=List[ArticleResponse])
async def get_articles(
    skip: int = 0,
    limit: int = 100,
    published_only: bool = True,
    db: Session = Depends(get_db),
):
    """Получить список всех статей"""
    articles = ArticleService(db).get_articles(
        skip=skip, limit=limit, published_only=published_only
    )
    return articles


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: str = Path(..., description="UUID статьи"),
    db: Session = Depends(get_db),
):
    """Получить статью по UUID"""
    # Валидируем UUID статьи
    validate_uuid(article_id, "UUID статьи")

    article = ArticleService(db).get_article(article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Статья не найдена"
        )
    return article


@router.post(
    "/", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED
)
async def create_article(
    article: ArticleCreate, db: Session = Depends(get_db)
):
    """Создать новую статью"""
    return ArticleService(db).create_article(article)


@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_update: ArticleUpdate,
    article_id: str = Path(..., description="UUID статьи"),
    db: Session = Depends(get_db),
):
    """Обновить статью по UUID"""
    # Валидируем UUID статьи
    validate_uuid(article_id, "UUID статьи")

    article = ArticleService(db).update_article(article_id, article_update)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Статья не найдена"
        )
    return article


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: str = Path(..., description="UUID статьи"),
    db: Session = Depends(get_db),
):
    """Удалить статью по UUID"""
    # Валидируем UUID статьи
    validate_uuid(article_id, "UUID статьи")

    success = ArticleService(db).delete_article(article_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Статья не найдена"
        )


@router.get("/search/{search_term}")
async def search_articles(
    search_term: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Поиск статей по заголовку или содержанию"""
    articles = ArticleService(db).search_articles(
        search_term, skip=skip, limit=limit
    )
    return articles
