# Import all the models, so that Base has them before being
# imported by Alembic
from app.catalog.models.item import Item  # noqa
from app.db.base_class import Base  # noqa
from app.news.models.article import Article  # noqa
from app.orders.models.order import Order, OrderItem  # noqa
from app.users.models.user import User  # noqa

__all__ = ["Base", "User", "Item", "Order", "OrderItem", "Article"]
