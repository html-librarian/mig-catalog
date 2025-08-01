from sqlalchemy import Column, String, Text, Numeric, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base import Base
import uuid


class Item(Base):
    __tablename__  =  "items"

    uuid = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name  =  Column(String(255), nullable = False, index = True)
    description  =  Column(Text, nullable = True)
    price  =  Column(Numeric(10, 2), nullable = False)
    category  =  Column(String(100), nullable = False, index = True)
    created_at  =  Column(DateTime, default = func.now())
    updated_at  =  Column(DateTime, default = func.now(), onupdate = func.now())

    # Отношения
    order_items = relationship("OrderItem", back_populates="item")

    def __repr__(self):
        return f"<Item(uuid={self.uuid}, name='{self.name}', price={self.price})>"
