"""
Сервис для работы с товарами
"""

from typing import Dict, List, Optional

from sqlalchemy import asc, desc, func, or_
from sqlalchemy.orm import Session

from app.catalog.models.item import Item
from app.catalog.schemas.item import ItemCreate, ItemUpdate
from app.core.cache import cache, invalidate_cache
from app.core.logging import get_logger
from app.core.validators import validate_item_data

logger = get_logger("item_service")


class ItemService:
    """Сервис для работы с товарами"""

    def __init__(self, db: Session):
        self.db = db

    @cache("item:get", ttl=300)  # 5 минут кэш
    def get_item(self, item_uuid: str) -> Optional[Item]:
        """Получить товар по UUID"""
        try:
            return self.db.query(Item).filter(Item.uuid == item_uuid).first()
        except Exception as e:
            logger.error(f"Error getting item {item_uuid}: {e}")
            return None

    @cache("item:list", ttl=180)  # 3 минуты кэш
    def get_items(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        search: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> List[Item]:
        """Получить список товаров с фильтрацией и сортировкой"""
        try:
            query = self.db.query(Item)

            # Фильтрация по категории
            if category:
                query = query.filter(Item.category == category)

            # Поиск по названию и описанию
            if search:
                search_filter = or_(
                    Item.name.ilike(f"%{search}%"),
                    Item.description.ilike(f"%{search}%"),
                )
                query = query.filter(search_filter)

            # Фильтрация по цене
            if min_price is not None:
                query = query.filter(Item.price >= min_price)
            if max_price is not None:
                query = query.filter(Item.price <= max_price)

            # Сортировка
            if sort_by == "price":
                order_column = Item.price
            elif sort_by == "name":
                order_column = Item.name
            elif sort_by == "category":
                order_column = Item.category
            else:
                order_column = Item.created_at

            if sort_order == "asc":
                query = query.order_by(asc(order_column))
            else:
                query = query.order_by(desc(order_column))

            # Пагинация
            query = query.offset(skip).limit(limit)

            return query.all()

        except Exception as e:
            logger.error(f"Error getting items: {e}")
            return []

    @cache("item:count", ttl=300)
    def get_items_count(
        self,
        category: Optional[str] = None,
        search: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
    ) -> int:
        """Получить количество товаров с фильтрацией"""
        try:
            query = self.db.query(Item)

            # Применяем те же фильтры
            if category:
                query = query.filter(Item.category == category)

            if search:
                search_filter = or_(
                    Item.name.ilike(f"%{search}%"),
                    Item.description.ilike(f"%{search}%"),
                )
                query = query.filter(search_filter)

            if min_price is not None:
                query = query.filter(Item.price >= min_price)
            if max_price is not None:
                query = query.filter(Item.price <= max_price)

            return query.count()

        except Exception as e:
            logger.error(f"Error counting items: {e}")
            return 0

    @cache("item:categories", ttl=600)  # 10 минут кэш
    def get_categories(self) -> List[str]:
        """Получить список всех категорий"""
        try:
            categories = self.db.query(Item.category).distinct().all()
            return [cat[0] for cat in categories if cat[0]]
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return []

    @cache("item:popular", ttl=180)
    def get_popular_items(self, limit: int = 10) -> List[Item]:
        """Получить популярные товары (по количеству заказов)"""
        try:
            # Здесь можно добавить логику определения популярности
            # Пока возвращаем последние добавленные товары
            return (
                self.db.query(Item)
                .order_by(desc(Item.created_at))
                .limit(limit)
                .all()
            )
        except Exception as e:
            logger.error(f"Error getting popular items: {e}")
            return []

    @invalidate_cache("item")
    def create_item(self, item_data: ItemCreate) -> Optional[Item]:
        """Создать новый товар"""
        try:
            # Валидация данных
            is_valid, errors = validate_item_data(
                item_data.name, item_data.price, item_data.category
            )

            if not is_valid:
                logger.error(f"Item validation failed: {errors}")
                raise ValueError(f"Validation errors: {', '.join(errors)}")

            # Создаем товар
            db_item = Item(
                name=item_data.name,
                description=item_data.description,
                price=item_data.price,
                category=item_data.category,
            )

            self.db.add(db_item)
            self.db.commit()
            self.db.refresh(db_item)

            logger.info(f"Created item: {db_item.uuid}")
            return db_item

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating item: {e}")
            raise

    @invalidate_cache("item")
    def update_item(
        self, item_uuid: str, item_data: ItemUpdate
    ) -> Optional[Item]:
        """Обновить товар"""
        try:
            db_item = self.get_item(item_uuid)
            if not db_item:
                return None

            # Валидация данных
            update_data = item_data.dict(exclude_unset=True)

            if (
                "name" in update_data
                or "price" in update_data
                or "category" in update_data
            ):
                name = update_data.get("name", db_item.name)
                price = update_data.get("price", db_item.price)
                category = update_data.get("category", db_item.category)

                is_valid, errors = validate_item_data(name, price, category)
                if not is_valid:
                    logger.error(f"Item validation failed: {errors}")
                    raise ValueError(f"Validation errors: {', '.join(errors)}")

            # Обновляем поля
            for field, value in update_data.items():
                setattr(db_item, field, value)

            self.db.commit()
            self.db.refresh(db_item)

            logger.info(f"Updated item: {item_uuid}")
            return db_item

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating item {item_uuid}: {e}")
            raise

    @invalidate_cache("item")
    def delete_item(self, item_uuid: str) -> bool:
        """Удалить товар"""
        try:
            db_item = self.get_item(item_uuid)
            if not db_item:
                return False

            self.db.delete(db_item)
            self.db.commit()

            logger.info(f"Deleted item: {item_uuid}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting item {item_uuid}: {e}")
            return False

    def search_items(self, query: str, limit: int = 20) -> List[Item]:
        """Поиск товаров по названию и описанию"""
        try:
            search_filter = or_(
                Item.name.ilike(f"%{query}%"),
                Item.description.ilike(f"%{query}%"),
                Item.category.ilike(f"%{query}%"),
            )

            return self.db.query(Item).filter(search_filter).limit(limit).all()

        except Exception as e:
            logger.error(f"Error searching items: {e}")
            return []

    def get_items_by_category(
        self, category: str, limit: int = 50
    ) -> List[Item]:
        """Получить товары по категории"""
        try:
            return (
                self.db.query(Item)
                .filter(Item.category == category)
                .limit(limit)
                .all()
            )

        except Exception as e:
            logger.error(f"Error getting items by category {category}: {e}")
            return []

    def get_price_range(self) -> Dict[str, float]:
        """Получить диапазон цен"""
        try:
            result = self.db.query(
                func.min(Item.price).label("min_price"),
                func.max(Item.price).label("max_price"),
            ).first()

            return {
                "min_price": (
                    float(result.min_price) if result.min_price else 0.0
                ),
                "max_price": (
                    float(result.max_price) if result.max_price else 0.0
                ),
            }

        except Exception as e:
            logger.error(f"Error getting price range: {e}")
            return {"min_price": 0.0, "max_price": 0.0}
