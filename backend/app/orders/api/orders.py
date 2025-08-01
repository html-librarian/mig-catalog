from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session
from typing import List
from pydantic import Field
from app.db.session import get_db
from app.orders.schemas.order import OrderCreate, OrderUpdate, OrderResponse
from app.orders.services.order_service import OrderService
from app.core.validators import validate_uuid, validate_uuid_optional

router  =  APIRouter(tags = ["orders"])


@router.get("/", response_model = List[OrderResponse])
async def get_orders(
    skip: int  =  0,
    limit: int  =  100,
    user_uuid: str  =  Query(None, description = "UUID пользователя для фильтрации"),
    db: Session  =  Depends(get_db)
):
    """Получить список всех заказов"""
    # Валидируем UUID пользователя, если он передан
    if user_uuid:
        validate_uuid(user_uuid, "UUID пользователя")

    orders  =  OrderService(db).get_orders(skip = skip, limit = limit, user_uuid = user_uuid)
    return orders


@router.get("/{order_id}", response_model = OrderResponse)
async def get_order(order_id: str  =  Path(..., description = "UUID заказа"), db: Session  =  Depends(get_db)):
    """Получить заказ по UUID"""
    # Валидируем UUID заказа
    validate_uuid(order_id, "UUID заказа")

    order  =  OrderService(db).get_order(order_id)
    if not order:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Заказ не найден"
        )
    return order


@router.post("/", response_model = OrderResponse, status_code = status.HTTP_201_CREATED)
async def create_order(order: OrderCreate, db: Session  =  Depends(get_db)):
    """Создать новый заказ"""
    return OrderService(db).create_order(order)


@router.put("/{order_id}", response_model = OrderResponse)
async def update_order(
    order_update: OrderUpdate,
    order_id: str  =  Path(..., description = "UUID заказа"),
    db: Session  =  Depends(get_db)
):
    """Обновить заказ по UUID"""
    # Валидируем UUID заказа
    validate_uuid(order_id, "UUID заказа")

    order  =  OrderService(db).update_order(order_id, order_update)
    if not order:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Заказ не найден"
        )
    return order


@router.delete("/{order_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: str  =  Path(..., description = "UUID заказа"), db: Session  =  Depends(get_db)):
    """Удалить заказ по UUID"""
    # Валидируем UUID заказа
    validate_uuid(order_id, "UUID заказа")

    success  =  OrderService(db).delete_order(order_id)
    if not success:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Заказ не найден"
        )
