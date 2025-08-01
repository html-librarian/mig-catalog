from decimal import Decimal
from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.catalog.models.item import Item
from app.orders.models.order import Order, OrderItem
from app.orders.schemas.order import OrderCreate, OrderUpdate


class OrderService:
    def __init__(self, db: Session):
        self.db = db

    def get_orders(
        self, skip: int = 0, limit: int = 100, user_uuid: Optional[str] = None
    ) -> List[Order]:
        """Получить список заказов"""
        query = self.db.query(Order)

        if user_uuid:
            query = query.filter(Order.user_uuid == user_uuid)

        return query.offset(skip).limit(limit).all()

    def get_user_orders(self, user_uuid: str) -> List[Order]:
        """Получить заказы пользователя"""
        return self.db.query(Order).filter(Order.user_uuid == user_uuid).all()

    def get_order(self, order_uuid: str) -> Optional[Order]:
        """Получить заказ по UUID"""
        return self.db.query(Order).filter(Order.uuid == order_uuid).first()

    def create_order(self, order: OrderCreate) -> Order:
        """Создать новый заказ"""
        # Проверяем, что все товары существуют
        item_uuids = [item.item_uuid for item in order.order_items]
        items = self.db.query(Item).filter(Item.uuid.in_(item_uuids)).all()

        if len(items) != len(item_uuids):
            raise ValueError("Некоторые товары не найдены")

        # Создаем заказ
        db_order = Order(
            user_uuid=order.user_uuid,
            total_amount=order.total_amount,
            status=order.status,
        )

        try:
            self.db.add(db_order)
            self.db.flush()  # Получаем UUID заказа

            # Создаем элементы заказа
            for order_item in order.order_items:
                db_order_item = OrderItem(
                    order_uuid=db_order.uuid,
                    item_uuid=order_item.item_uuid,
                    quantity=order_item.quantity,
                    price=order_item.price,
                )
                self.db.add(db_order_item)

            self.db.commit()
            self.db.refresh(db_order)
            return db_order
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Ошибка при создании заказа")

    def update_order(
        self, order_uuid: str, order_update: OrderUpdate
    ) -> Optional[Order]:
        """Обновить заказ"""
        db_order = self.get_order(order_uuid)
        if not db_order:
            return None

        update_data = order_update.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_order, field, value)

        try:
            self.db.commit()
            self.db.refresh(db_order)
            return db_order
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Ошибка при обновлении заказа")

    def delete_order(self, order_uuid: str) -> bool:
        """Удалить заказ"""
        db_order = self.get_order(order_uuid)
        if not db_order:
            return False

        self.db.delete(db_order)
        self.db.commit()
        return True

    def calculate_order_total(self, order_items: List[dict]) -> Decimal:
        """Рассчитать общую сумму заказа"""
        total = Decimal("0")
        for item in order_items:
            total += item["price"] * item["quantity"]
        return total
