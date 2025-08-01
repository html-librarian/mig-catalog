import uuid

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Item(Base):
    __tablename__ = "items"

    uuid = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Отношения
    order_items = relationship("OrderItem", back_populates="item")

    # Ограничения для валидации данных
    __table_args__ = (
        CheckConstraint("price >= 0", name="check_price_positive"),
        CheckConstraint("length(name) >= 1", name="check_name_not_empty"),
        CheckConstraint(
            "length(category) >= 1", name="check_category_not_empty"
        ),
        CheckConstraint("length(name) <= 255", name="check_name_length"),
        CheckConstraint(
            "length(category) <= 100", name="check_category_length"
        ),
    )

    def __repr__(self):
        return (
            f"<Item(uuid={self.uuid}, name='{self.name}', price={self.price})>"
        )

    def validate(self):
        """Валидация данных модели"""
        errors = []

        if not self.name or not self.name.strip():
            errors.append("Название товара не может быть пустым")

        if len(self.name) > 255:
            errors.append("Название товара не может превышать 255 символов")

        if not self.category or not self.category.strip():
            errors.append("Категория не может быть пустой")

        if len(self.category) > 100:
            errors.append("Категория не может превышать 100 символов")

        if self.price < 0:
            errors.append("Цена не может быть отрицательной")

        if self.price > 99999999.99:
            errors.append("Цена не может превышать 99,999,999.99")

        return errors
