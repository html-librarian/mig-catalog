from math import ceil
from typing import Generic, List, Optional, TypeVar

from fastapi import Query
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Параметры пагинации"""

    page: int = Field(1, ge=1, description="Номер страницы")
    size: int = Field(10, ge=1, le=100, description="Размер страницы")

    @property
    def skip(self) -> int:
        """Количество записей для пропуска"""
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        """Лимит записей"""
        return self.size


class PaginatedResponse(BaseModel, Generic[T]):
    """Ответ с пагинацией"""

    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool

    @classmethod
    def create(
        cls, items: List[T], total: int, page: int, size: int
    ) -> "PaginatedResponse[T]":
        """Создать ответ с пагинацией"""
        pages = ceil(total / size) if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1,
        )


def get_pagination_params(
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(10, ge=1, le=100, description="Размер страницы"),
) -> PaginationParams:
    """Получить параметры пагинации из запроса"""
    return PaginationParams(page=page, size=size)


class PaginationHelper:
    """Хелпер для работы с пагинацией"""

    @staticmethod
    def get_offset(page: int, size: int) -> int:
        """Получить смещение для SQL запроса"""
        return (page - 1) * size

    @staticmethod
    def get_limit(size: int) -> int:
        """Получить лимит для SQL запроса"""
        return size

    @staticmethod
    def calculate_pages(total: int, size: int) -> int:
        """Вычислить общее количество страниц"""
        return ceil(total / size) if total > 0 else 0

    @staticmethod
    def has_next_page(page: int, total_pages: int) -> bool:
        """Проверить, есть ли следующая страница"""
        return page < total_pages

    @staticmethod
    def has_prev_page(page: int) -> bool:
        """Проверить, есть ли предыдущая страница"""
        return page > 1

    @staticmethod
    def get_page_info(page: int, size: int, total: int) -> dict:
        """Получить информацию о странице"""
        total_pages = PaginationHelper.calculate_pages(total, size)

        return {
            "current_page": page,
            "page_size": size,
            "total_items": total,
            "total_pages": total_pages,
            "has_next": PaginationHelper.has_next_page(page, total_pages),
            "has_prev": PaginationHelper.has_prev_page(page),
            "offset": PaginationHelper.get_offset(page, size),
            "limit": PaginationHelper.get_limit(size),
        }


class CursorPaginationParams(BaseModel):
    """Параметры курсорной пагинации"""

    cursor: Optional[str] = None
    limit: int = Field(10, ge=1, le=100, description="Количество записей")


class CursorPaginatedResponse(BaseModel, Generic[T]):
    """Ответ с курсорной пагинацией"""

    items: List[T]
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None
    has_more: bool = False


def get_cursor_pagination_params(
    cursor: Optional[str] = Query(None, description="Курсор для пагинации"),
    limit: int = Query(10, ge=1, le=100, description="Количество записей"),
) -> CursorPaginationParams:
    """Получить параметры курсорной пагинации из запроса"""
    return CursorPaginationParams(cursor=cursor, limit=limit)
