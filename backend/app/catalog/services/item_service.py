from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.catalog.models.item import Item
from app.catalog.schemas.item import ItemCreate, ItemUpdate


class ItemService:
    def __init__(self, db: Session):
        self.db  =  db

    def get_items(self, skip: int = 0, limit: int = 100, category: Optional[str] = None) -> List[Item]:
        """Получить список товаров"""
        query  =  self.db.query(Item)

        if category:
            query  =  query.filter(Item.category == category)

        return query.offset(skip).limit(limit).all()

    def get_item(self, item_uuid: str) -> Optional[Item]:
        """Получить товар по UUID"""
        return self.db.query(Item).filter(Item.uuid == item_uuid).first()

    def create_item(self, item: ItemCreate) -> Item:
        """Создать новый товар"""
        db_item  =  Item(**item.dict())

        try:
            self.db.add(db_item)
            self.db.commit()
            self.db.refresh(db_item)
            return db_item
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Ошибка при создании товара")

    def update_item(self, item_uuid: str, item_update: ItemUpdate) -> Optional[Item]:
        """Обновить товар"""
        db_item  =  self.get_item(item_uuid)
        if not db_item:
            return None

        update_data  =  item_update.dict(exclude_unset = True)

        for field, value in update_data.items():
            setattr(db_item, field, value)

        try:
            self.db.commit()
            self.db.refresh(db_item)
            return db_item
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Ошибка при обновлении товара")

    def delete_item(self, item_uuid: str) -> bool:
        """Удалить товар"""
        db_item  =  self.get_item(item_uuid)
        if not db_item:
            return False

        self.db.delete(db_item)
        self.db.commit()
        return True

    def get_categories(self) -> List[str]:
        """Получить список всех категорий"""
        categories  =  self.db.query(Item.category).distinct().all()
        return [category[0] for category in categories]

    def search_items(self, search_term: str, skip: int  =  0, limit: int  =  100) -> List[Item]:
        """Поиск товаров по названию или описанию"""
        return self.db.query(Item).filter(
            (Item.name.ilike(f"%{search_term}%")) |
            (Item.description.ilike(f"%{search_term}%"))
        ).offset(skip).limit(limit).all()
