#!/usr/bin/env python3
"""
Скрипт для генерации безопасных секретных ключей
Используйте этот скрипт для создания ключей для продакшена
"""

import secrets
import hashlib
import os
from datetime import datetime


def generate_secret_key(length: int = 64) -> str:
    """Генерирует криптографически безопасный секретный ключ"""
    return secrets.token_urlsafe(length)


def generate_rotation_key(length: int = 64) -> str:
    """Генерирует ключ для ротации"""
    return secrets.token_urlsafe(length)


def generate_database_password(length: int = 32) -> str:
    """Генерирует безопасный пароль для базы данных"""
    return secrets.token_urlsafe(length)


def generate_redis_password(length: int = 32) -> str:
    """Генерирует безопасный пароль для Redis"""
    return secrets.token_urlsafe(length)


def create_env_file():
    """Создает файл .env с безопасными ключами"""
    print("🔐 Генерация безопасных ключей для MIG Catalog API")
    print("=" * 60)
    
    # Генерируем ключи
    secret_key = generate_secret_key(64)
    rotation_key = generate_rotation_key(64)
    db_password = generate_database_password(32)
    redis_password = generate_redis_password(32)
    
    # Создаем содержимое файла .env
    env_content = f"""# =============================================================================
# MIG CATALOG API - БЕЗОПАСНЫЕ НАСТРОЙКИ
# =============================================================================
# Сгенерировано: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# ВНИМАНИЕ: Храните этот файл в безопасном месте!
# =============================================================================

# =============================================================================
# ОСНОВНЫЕ НАСТРОЙКИ
# =============================================================================
APP_NAME=MIG Catalog API
APP_VERSION=1.3.0
DEBUG=False
ENVIRONMENT=production

# =============================================================================
# БАЗА ДАННЫХ
# =============================================================================
DATABASE_URL=postgresql://mig_user:{db_password}@localhost:5432/mig_catalog
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_RECYCLE=3600
DB_POOL_TIMEOUT=30

# =============================================================================
# REDIS
# =============================================================================
REDIS_URL=redis://:mig_redis_{redis_password}@localhost:6379

# =============================================================================
# БЕЗОПАСНОСТЬ - КРИТИЧНО!
# =============================================================================
SECRET_KEY={secret_key}
ROTATION_SECRET_KEY={rotation_key}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# =============================================================================
# CORS НАСТРОЙКИ
# =============================================================================
# В продакшене укажите только ваши домены
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# =============================================================================
# ЛОГИРОВАНИЕ
# =============================================================================
LOG_LEVEL=INFO
LOG_FORMAT=json

# =============================================================================
# RATE LIMITING
# =============================================================================
RATE_LIMIT_ENABLED=True
RATE_LIMIT_DEFAULT=100
RATE_LIMIT_WINDOW=60

# =============================================================================
# КЭШИРОВАНИЕ
# =============================================================================
CACHE_TTL=3600
CACHE_ENABLED=True

# =============================================================================
# МОНИТОРИНГ
# =============================================================================
METRICS_ENABLED=True
HEALTH_CHECK_ENABLED=True

# =============================================================================
# ДОПОЛНИТЕЛЬНЫЕ НАСТРОЙКИ БЕЗОПАСНОСТИ
# =============================================================================
MAX_LOGIN_ATTEMPTS=5
LOGIN_LOCKOUT_DURATION=300
SESSION_TIMEOUT_MINUTES=60
MIN_PASSWORD_LENGTH=8
REQUIRE_SPECIAL_CHARS=True
REQUIRE_NUMBERS=True
REQUIRE_UPPERCASE=True
"""
    
    # Записываем в файл
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Файл .env создан с безопасными ключами")
    print("=" * 60)
    print("🔑 Сгенерированные ключи:")
    print(f"SECRET_KEY: {secret_key[:20]}...")
    print(f"ROTATION_SECRET_KEY: {rotation_key[:20]}...")
    print(f"DB_PASSWORD: {db_password}")
    print(f"REDIS_PASSWORD: {redis_password}")
    print("=" * 60)
    print("⚠️  ВАЖНО:")
    print("1. Сохраните этот файл в безопасном месте")
    print("2. Не коммитьте .env файл в git")
    print("3. Измените пароли базы данных и Redis")
    print("4. Настройте CORS для ваших доменов")
    print("5. Включите HTTPS в продакшене")
    print("=" * 60)


def create_production_script():
    """Создает скрипт для настройки продакшена"""
    script_content = """#!/bin/bash
# =============================================================================
# СКРИПТ НАСТРОЙКИ ПРОДАКШЕНА MIG CATALOG API
# =============================================================================

echo "🚀 Настройка продакшена MIG Catalog API"
echo "========================================"

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден!"
    echo "Запустите: python generate_secrets.py"
    exit 1
fi

# Создаем пользователя базы данных
echo "📊 Настройка базы данных..."
sudo -u postgres psql -c "CREATE USER mig_user WITH PASSWORD '$(grep DB_PASSWORD .env | cut -d'=' -f2)';"
sudo -u postgres psql -c "CREATE DATABASE mig_catalog OWNER mig_user;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE mig_catalog TO mig_user;"

# Настраиваем Redis
echo "🔴 Настройка Redis..."
sudo systemctl enable redis
sudo systemctl start redis

# Создаем пользователя для приложения
echo "👤 Создание пользователя приложения..."
sudo useradd -r -s /bin/false mig_app
sudo mkdir -p /opt/mig-catalog
sudo chown mig_app:mig_app /opt/mig-catalog

# Копируем файлы
echo "📁 Копирование файлов..."
sudo cp -r . /opt/mig-catalog/
sudo chown -R mig_app:mig_app /opt/mig-catalog/

# Создаем systemd сервис
echo "🔧 Создание systemd сервиса..."
sudo tee /etc/systemd/system/mig-catalog.service > /dev/null <<EOF
[Unit]
Description=MIG Catalog API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=mig_app
Group=mig_app
WorkingDirectory=/opt/mig-catalog/backend
Environment=PATH=/opt/mig-catalog/backend/venv/bin
ExecStart=/opt/mig-catalog/backend/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Включаем и запускаем сервис
echo "🚀 Запуск сервиса..."
sudo systemctl daemon-reload
sudo systemctl enable mig-catalog
sudo systemctl start mig-catalog

echo "✅ Настройка завершена!"
echo "📊 Статус сервиса: sudo systemctl status mig-catalog"
echo "📝 Логи: sudo journalctl -u mig-catalog -f"
"""
    
    with open('setup_production.sh', 'w') as f:
        f.write(script_content)
    
    os.chmod('setup_production.sh', 0o755)
    print("✅ Скрипт setup_production.sh создан")
    print("Запустите: sudo ./setup_production.sh")


def main():
    """Основная функция"""
    print("🔐 Генератор безопасных ключей MIG Catalog API")
    print("=" * 60)
    
    choice = input("Выберите действие:\n1. Создать .env файл\n2. Создать скрипт продакшена\n3. Все\nВаш выбор (1-3): ")
    
    if choice == "1":
        create_env_file()
    elif choice == "2":
        create_production_script()
    elif choice == "3":
        create_env_file()
        create_production_script()
    else:
        print("❌ Неверный выбор")
        return
    
    print("\n🎉 Готово! Теперь настройте продакшен безопасно.")


if __name__ == "__main__":
    main() 