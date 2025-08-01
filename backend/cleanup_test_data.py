#!/usr/bin/env python3
"""
Скрипт для очистки тестовых данных из базы данных
"""

import os
import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from app.db.session import SessionLocal, engine

def cleanup_test_data():
    """Очищает тестовые данные из базы данных"""
    print("🧹 Очистка тестовых данных...")
    
    db = SessionLocal()
    try:
        # Удаляем пользователей с вредоносными именами
        malicious_usernames = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "admin'--",
            "'; INSERT INTO users VALUES ('hacker', 'hacker@evil.com'); --"
        ]
        
        for username in malicious_usernames:
            db.execute(
                text("DELETE FROM users WHERE username = :username"),
                {"username": username}
            )
        
        # Удаляем тестовых пользователей
        db.execute(
            text("DELETE FROM users WHERE email LIKE 'test%@example.com'")
        )
        
        # Удаляем тестовые товары
        db.execute(
            text("DELETE FROM items WHERE name LIKE '%<script>%' OR name LIKE '%javascript:%'")
        )
        
        db.commit()
        print("✅ Тестовые данные очищены")
        
    except Exception as e:
        print(f"❌ Ошибка при очистке: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_test_data() 