import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class Order(Base):
    """Модель заказа"""

    __tablename__ = "orders"

    uuid = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    user_uuid = Column(String(36), ForeignKey("users.uuid"), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Отношения
    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")

    def __repr__(self):
        return (
            f"<Order(uuid = {self.uuid}, "
            f"user_uuid = {self.user_uuid}, "
            f"total_amount = {self.total_amount})>"
        )


class OrderItem(Base):
    """Модель элемента заказа"""

    __tablename__ = "order_items"

    uuid = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    order_uuid = Column(String(36), ForeignKey("orders.uuid"), nullable=False)
    item_uuid = Column(String(36), ForeignKey("items.uuid"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Отношения
    order = relationship("Order", back_populates="order_items")
    item = relationship("Item", back_populates="order_items")

    def __repr__(self):
        return (
            f"<OrderItem(uuid={self.uuid}, "
            f"order_uuid={self.order_uuid}, "
            f"item_uuid={self.item_uuid})>"
        )
