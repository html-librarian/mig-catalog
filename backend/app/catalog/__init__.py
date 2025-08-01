"""
Каталог товаров - основной модуль для работы с товарами
"""

from .api.items import router as items_router
from .models.item import Item
from .schemas.item import ItemCreate, ItemUpdate, ItemResponse
from .services.item_service import ItemService

__all__  =  [
    "items_router",
    "Item",
    "ItemCreate",
    "ItemUpdate",
    "ItemResponse",
    "ItemService",
]
