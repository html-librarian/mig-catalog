# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.session import Base
from app.users.models.user import User
from app.catalog.models.item import Item
from app.orders.models.order import Order, OrderItem
from app.news.models.article import Article

__all__  =  ["Base", "User", "Item", "Order", "OrderItem", "Article"]
