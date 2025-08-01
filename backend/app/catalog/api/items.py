from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.catalog.schemas.item import ItemCreate, ItemUpdate, ItemResponse
from app.catalog.services.item_service import ItemService
from app.core.validators import validate_uuid

router = APIRouter(tags=["items"])


@router.get("/", response_model = List[ItemResponse])
async def get_items(
    skip: int  =  0,
    limit: int  =  100,
    db: Session  =  Depends(get_db)
):
    """Получить список всех товаров"""
    items  =  ItemService(db).get_items(skip = skip, limit = limit)
    return items


@router.get("/{item_id}", response_model = ItemResponse)
async def get_item(
    item_id: str  =  Path(..., description = "UUID товара"),
    db: Session  =  Depends(get_db)
):
    """Получить товар по UUID"""
    # Валидируем UUID
    validate_uuid(item_id, "UUID товара")

    item  =  ItemService(db).get_item(item_id)
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Товар не найден"
        )
    return item


@router.post("/", response_model = ItemResponse)
async def create_item(
    item: ItemCreate,
    db: Session  =  Depends(get_db)
):
    """Создать новый товар"""
    return ItemService(db).create_item(item)


@router.put("/{item_id}", response_model = ItemResponse)
async def update_item(
    item_id: str  =  Path(..., description = "UUID товара"),
    item: Optional[ItemUpdate] = None,
    db: Session  =  Depends(get_db)
):
    """Обновить товар по UUID"""
    # Валидируем UUID
    validate_uuid(item_id, "UUID товара")

    updated_item  =  ItemService(db).update_item(item_id, item)
    if not updated_item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Товар не найден"
        )
    return updated_item


@router.delete("/{item_id}")
async def delete_item(
    item_id: str  =  Path(..., description = "UUID товара"),
    db: Session  =  Depends(get_db)
):
    """Удалить товар по UUID"""
    # Валидируем UUID
    validate_uuid(item_id, "UUID товара")

    success  =  ItemService(db).delete_item(item_id)
    if not success:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Товар не найден"
        )
    return {"message": "Товар успешно удален"}
