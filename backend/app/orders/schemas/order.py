from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class OrderItemBase(BaseModel):
    item_uuid: str  =  Field(..., description = "UUID товара")
    quantity: int  =  Field(..., gt = 0)
    price: Decimal  =  Field(..., ge = 0)


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    uuid: str  =  Field(..., description = "UUID элемента заказа")
    order_uuid: str  =  Field(..., description = "UUID заказа")
    created_at: datetime

    class Config:
        from_attributes  =  True


class OrderBase(BaseModel):
    user_uuid: str  =  Field(..., description = "UUID пользователя")
    total_amount: Decimal  =  Field(..., ge = 0)
    status: str  =  Field(default = "pending", max_length = 50)


class OrderCreate(OrderBase):
    order_items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    total_amount: Optional[Decimal]  =  Field(None, ge = 0)
    status: Optional[str]  =  Field(None, max_length = 50)


class OrderResponse(OrderBase):
    uuid: str  =  Field(..., description = "UUID заказа")
    created_at: datetime
    updated_at: Optional[datetime]  =  None
    order_items: List[OrderItemResponse]  =  []

    class Config:
        from_attributes  =  True
