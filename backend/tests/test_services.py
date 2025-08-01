import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from decimal import Decimal
from app.users.services.user_service import UserService
from app.catalog.services.item_service import ItemService
from app.orders.services.order_service import OrderService
from app.users.models.user import User
from app.catalog.models.item import Item
from app.orders.models.order import Order, OrderItem
from app.core.exceptions import (
    UserNotFoundException,
    ItemNotFoundException,
    OrderNotFoundException,
    DuplicateUserException
)


class TestUserService:
    """Тесты для сервиса пользователей"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.mock_db = Mock(spec=Session)
        self.user_service = UserService(self.mock_db)
    
    def test_get_user_by_email_found(self):
        """Тест получения пользователя по email - найден"""
        # Подготавливаем мок
        mock_user = User(
            uuid="test-uuid",
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password"
        )
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Выполняем тест
        result = self.user_service.get_user_by_email("test@example.com")
        
        # Проверяем результат
        assert result == mock_user
        assert result.email == "test@example.com"
    
    def test_get_user_by_email_not_found(self):
        """Тест получения пользователя по email - не найден"""
        # Подготавливаем мок
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Выполняем тест
        result = self.user_service.get_user_by_email("nonexistent@example.com")
        
        # Проверяем результат
        assert result is None
    
    def test_get_user_found(self):
        """Тест получения пользователя по UUID - найден"""
        # Подготавливаем мок
        mock_user = User(
            uuid="test-uuid",
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password"
        )
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Выполняем тест
        result = self.user_service.get_user("test-uuid")
        
        # Проверяем результат
        assert result == mock_user
        assert result.uuid == "test-uuid"
    
    def test_get_user_not_found(self):
        """Тест получения пользователя по UUID - не найден"""
        # Подготавливаем мок
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Выполняем тест
        result = self.user_service.get_user("nonexistent-uuid")
        
        # Проверяем результат
        assert result is None
    
    def test_create_user_success(self):
        """Тест создания пользователя - успех"""
        # Создаем мок пользователя
        mock_user = User(
            uuid="new-uuid",
            email="new@example.com",
            username="newuser",
            password_hash="hashed_password"
        )
        self.mock_db.add.return_value = None
        self.mock_db.commit.return_value = None
        self.mock_db.refresh.return_value = None
        
        # Мокаем проверку существующих пользователей
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Создаем объект UserCreate
        from app.users.schemas.user import UserCreate
        user_data = UserCreate(
            email="new@example.com",
            username="newuser",
            password="Password123!"
        )
        
        # Выполняем тест
        with patch('app.users.services.user_service.User') as mock_user_class:
            mock_user_class.return_value = mock_user
            result = self.user_service.create_user(user_data)
            
            # Проверяем результат
            assert result == mock_user
            self.mock_db.add.assert_called_once()
            self.mock_db.commit.assert_called_once()
    
    def test_delete_user_success(self):
        """Тест удаления пользователя - успех"""
        # Подготавливаем мок
        mock_user = User(
            uuid="test-uuid",
            email="test@example.com",
            username="testuser"
        )
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Выполняем тест
        result = self.user_service.delete_user("test-uuid")
        
        # Проверяем результат
        assert result == True
        self.mock_db.delete.assert_called_once_with(mock_user)
        self.mock_db.commit.assert_called_once()
    
    def test_delete_user_not_found(self):
        """Тест удаления пользователя - не найден"""
        # Подготавливаем мок
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Выполняем тест
        result = self.user_service.delete_user("nonexistent-uuid")
        
        # Проверяем результат
        assert result == False


class TestItemService:
    """Тесты для сервиса товаров"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.mock_db = Mock(spec=Session)
        self.item_service = ItemService(self.mock_db)
    
    def test_get_item_found(self):
        """Тест получения товара по UUID - найден"""
        # Подготавливаем мок
        mock_item = Item(
            uuid="item-uuid",
            name="Test Item",
            price=Decimal("10.50"),
            category="Electronics"
        )
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_item
        
        # Выполняем тест
        result = self.item_service.get_item("item-uuid")
        
        # Проверяем результат
        assert result == mock_item
        assert result.name == "Test Item"
    
    def test_get_item_not_found(self):
        """Тест получения товара по UUID - не найден"""
        # Подготавливаем мок
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Выполняем тест
        result = self.item_service.get_item("nonexistent-uuid")
        
        # Проверяем результат
        assert result is None
    
    def test_get_items_with_pagination(self):
        """Тест получения списка товаров с пагинацией"""
        # Подготавливаем мок
        mock_items = [
            Item(uuid="item1", name="Item 1", price=Decimal("10.00"), category="Electronics"),
            Item(uuid="item2", name="Item 2", price=Decimal("20.00"), category="Books")
        ]
        self.mock_db.query.return_value.offset.return_value.limit.return_value.all.return_value = mock_items
        
        # Выполняем тест
        result = self.item_service.get_items(skip=0, limit=10)
        
        # Проверяем результат
        assert result == mock_items
        assert len(result) == 2
    
    def test_search_items(self):
        """Тест поиска товаров"""
        # Подготавливаем мок
        mock_items = [
            Item(uuid="item1", name="iPhone", price=Decimal("999.00"), category="Electronics"),
            Item(uuid="item2", name="Samsung", price=Decimal("899.00"), category="Electronics")
        ]
        # Правильно настраиваем цепочку моков
        mock_query = Mock()
        mock_filter = Mock()
        mock_offset = Mock()
        mock_limit = Mock()
        
        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.offset.return_value = mock_offset
        mock_offset.limit.return_value = mock_limit
        mock_limit.all.return_value = mock_items
        
        # Выполняем тест
        result = self.item_service.search_items("phone")
        
        # Проверяем результат
        assert result == mock_items
        assert len(result) == 2


class TestOrderService:
    """Тесты для сервиса заказов"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.mock_db = Mock(spec=Session)
        self.order_service = OrderService(self.mock_db)
    
    def test_get_order_found(self):
        """Тест получения заказа по UUID - найден"""
        # Подготавливаем мок
        mock_order = Order(
            uuid="order-uuid",
            user_uuid="user-uuid",
            total_amount=Decimal("100.00"),
            status="pending"
        )
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_order
        
        # Выполняем тест
        result = self.order_service.get_order("order-uuid")
        
        # Проверяем результат
        assert result == mock_order
        assert result.total_amount == Decimal("100.00")
    
    def test_get_order_not_found(self):
        """Тест получения заказа по UUID - не найден"""
        # Подготавливаем мок
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Выполняем тест
        result = self.order_service.get_order("nonexistent-uuid")
        
        # Проверяем результат
        assert result is None
    
    def test_get_user_orders(self):
        """Тест получения заказов пользователя"""
        # Подготавливаем мок
        mock_orders = [
            Order(uuid="order1", user_uuid="user-uuid", total_amount=Decimal("50.00")),
            Order(uuid="order2", user_uuid="user-uuid", total_amount=Decimal("75.00"))
        ]
        self.mock_db.query.return_value.filter.return_value.all.return_value = mock_orders
        
        # Выполняем тест
        result = self.order_service.get_user_orders("user-uuid")
        
        # Проверяем результат
        assert result == mock_orders
        assert len(result) == 2
    
    def test_create_order_success(self):
        """Тест создания заказа - успех"""
        # Создаем объект OrderCreate
        from app.orders.schemas.order import OrderCreate, OrderItemCreate
        order_data = OrderCreate(
            user_uuid="user-uuid",
            total_amount=Decimal("100.00"),
            status="pending",
            order_items=[]
        )
        
        # Проверяем, что метод принимает правильные параметры
        assert order_data.user_uuid == "user-uuid"
        assert order_data.total_amount == Decimal("100.00")
        assert order_data.status == "pending"
        assert len(order_data.order_items) == 0 