#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных PostgreSQL
"""

import os
import sys
import uuid
from dotenv import load_dotenv
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Загружаем переменные окружения
load_dotenv()

def create_database():
    """Создание базы данных"""
    print("🔧 Создание базы данных...")
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL не найден в переменных окружения")
        return False
    
    try:
        # Парсим URL для получения параметров подключения
        if database_url.startswith("postgresql://"):
            connection_string = database_url.replace("postgresql://", "")
            
            if "@" in connection_string:
                auth_part, host_part = connection_string.split("@", 1)
                if ":" in auth_part:
                    username, password = auth_part.split(":", 1)
                else:
                    username = auth_part
                    password = ""
                
                if "/" in host_part:
                    host_port, database_name = host_part.split("/", 1)
                    if ":" in host_port:
                        host, port = host_port.split(":", 1)
                    else:
                        host = host_port
                        port = "5432"
                else:
                    host = host_part
                    port = "5432"
                    database_name = ""
            else:
                print("❌ Неверный формат DATABASE_URL")
                return False
            
            print(f"📊 Параметры подключения:")
            print(f"   Host: {host}")
            print(f"   Port: {port}")
            print(f"   Database: {database_name}")
            print(f"   Username: {username}")
            
            # Подключаемся к PostgreSQL без указания базы данных
            conn = psycopg2.connect(
                host=host,
                port=port,
                database="postgres",  # Подключаемся к системной базе
                user=username,
                password=password
            )
            
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Проверяем, существует ли база данных
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (database_name,))
            exists = cursor.fetchone()
            
            if exists:
                print(f"✅ База данных '{database_name}' уже существует")
            else:
                print(f"🔧 Создание базы данных '{database_name}'...")
                cursor.execute(f"CREATE DATABASE {database_name};")
                print(f"✅ База данных '{database_name}' создана успешно")
            
            cursor.close()
            conn.close()
            return True
            
    except psycopg2.Error as e:
        print(f"❌ Ошибка создания базы данных: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

def create_tables():
    """Создание таблиц"""
    print("\n🔧 Создание таблиц...")
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL не найден в переменных окружения")
        return False
    
    try:
        # Создаем движок SQLAlchemy
        engine = create_engine(database_url)
        
        # SQL для создания таблиц
        create_tables_sql = """
        -- Таблица пользователей
        CREATE TABLE IF NOT EXISTS users (
            uuid VARCHAR(36) PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            username VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Таблица товаров
        CREATE TABLE IF NOT EXISTS items (
            uuid VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            price DECIMAL(10,2) NOT NULL,
            category VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Таблица заказов
        CREATE TABLE IF NOT EXISTS orders (
            uuid VARCHAR(36) PRIMARY KEY,
            user_uuid VARCHAR(36) REFERENCES users(uuid),
            total_amount DECIMAL(10,2) NOT NULL,
            status VARCHAR(50) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Таблица элементов заказа
        CREATE TABLE IF NOT EXISTS order_items (
            uuid VARCHAR(36) PRIMARY KEY,
            order_uuid VARCHAR(36) REFERENCES orders(uuid),
            item_uuid VARCHAR(36) REFERENCES items(uuid),
            quantity INTEGER NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Таблица статей
        CREATE TABLE IF NOT EXISTS articles (
            uuid VARCHAR(36) PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            author VARCHAR(100) NOT NULL,
            is_published BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Индексы для улучшения производительности
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        CREATE INDEX IF NOT EXISTS idx_users_uuid ON users(uuid);
        CREATE INDEX IF NOT EXISTS idx_items_category ON items(category);
        CREATE INDEX IF NOT EXISTS idx_items_uuid ON items(uuid);
        CREATE INDEX IF NOT EXISTS idx_orders_user_uuid ON orders(user_uuid);
        CREATE INDEX IF NOT EXISTS idx_orders_uuid ON orders(uuid);
        CREATE INDEX IF NOT EXISTS idx_order_items_order_uuid ON order_items(order_uuid);
        CREATE INDEX IF NOT EXISTS idx_order_items_uuid ON order_items(uuid);
        CREATE INDEX IF NOT EXISTS idx_articles_uuid ON articles(uuid);
        CREATE INDEX IF NOT EXISTS idx_articles_title ON articles(title);
        """
        
        with engine.connect() as connection:
            # Выполняем SQL команды
            for statement in create_tables_sql.split(';'):
                if statement.strip():
                    connection.execute(text(statement))
            
            connection.commit()
            
            print("✅ Таблицы созданы успешно")
            
            # Проверяем созданные таблицы
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = result.fetchall()
            
            print(f"📋 Созданные таблицы:")
            for table in tables:
                print(f"   - {table[0]}")
        
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ Ошибка создания таблиц: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

def insert_sample_data():
    """Вставка тестовых данных"""
    print("\n🔧 Вставка тестовых данных...")
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL не найден в переменных окружения")
        return False
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            # Проверяем, есть ли уже данные
            result = connection.execute(text("SELECT COUNT(*) FROM items;"))
            items_count = result.fetchone()[0]
            
            if items_count > 0:
                print("✅ Тестовые данные уже существуют")
                return True
            
            # Вставляем тестовые товары
            import uuid
            
            sample_items = [
                (str(uuid.uuid4()), "Ноутбук Dell XPS 13", "Мощный ноутбук для работы и учебы", 89999.99, "Электроника"),
                (str(uuid.uuid4()), "Смартфон iPhone 15", "Новейший iPhone с отличной камерой", 79999.99, "Электроника"),
                (str(uuid.uuid4()), "Книга 'Python для начинающих'", "Учебник по программированию", 1299.99, "Книги"),
                (str(uuid.uuid4()), "Кофемашина DeLonghi", "Автоматическая кофемашина", 45999.99, "Бытовая техника"),
                (str(uuid.uuid4()), "Беговые кроссовки Nike", "Удобные кроссовки для бега", 8999.99, "Спорт"),
            ]
            
            for item_uuid, name, description, price, category in sample_items:
                connection.execute(text("""
                    INSERT INTO items (uuid, name, description, price, category)
                    VALUES (:uuid, :name, :description, :price, :category)
                """), {
                    "uuid": item_uuid,
                    "name": name,
                    "description": description,
                    "price": price,
                    "category": category
                })
            
            # Вставляем тестового пользователя
            admin_uuid = str(uuid.uuid4())
            connection.execute(text("""
                INSERT INTO users (uuid, email, username, password_hash, is_active)
                VALUES (:uuid, :email, :username, :password_hash, :is_active)
                ON CONFLICT (email) DO NOTHING
            """), {
                "uuid": admin_uuid,
                "email": "admin@mig-catalog.com",
                "username": "admin",
                "password_hash": "hashed_password_here",  # В реальном проекте хешируйте пароль!
                "is_active": True
            })
            
            # Вставляем тестовую статью
            article_uuid = str(uuid.uuid4())
            connection.execute(text("""
                INSERT INTO articles (uuid, title, content, author, is_published)
                VALUES (:uuid, :title, :content, :author, :is_published)
            """), {
                "uuid": article_uuid,
                "title": "Добро пожаловать в MIG Catalog",
                "content": "Это первая статья в нашем каталоге товаров. Здесь вы найдете лучшие товары по выгодным ценам.",
                "author": "Администратор",
                "is_published": True
            })
            
            connection.commit()
            print("✅ Тестовые данные добавлены успешно")
        
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ Ошибка вставки тестовых данных: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

def main():
    """Основная функция"""
    print("🚀 Инициализация базы данных MIG Catalog")
    print("=" * 50)
    
    # Создаем базу данных
    db_created = create_database()
    
    if not db_created:
        print("❌ Не удалось создать базу данных")
        return
    
    # Создаем таблицы
    tables_created = create_tables()
    
    if not tables_created:
        print("❌ Не удалось создать таблицы")
        return
    
    # Вставляем тестовые данные
    data_inserted = insert_sample_data()
    
    print("\n" + "=" * 50)
    
    if db_created and tables_created and data_inserted:
        print("🎉 База данных инициализирована успешно!")
        print("✅ Готово к использованию")
    else:
        print("❌ Произошли ошибки при инициализации")
        print("💡 Проверьте логи выше")

if __name__ == "__main__":
    main() 