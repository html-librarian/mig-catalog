#!/usr/bin/env python3
"""
Скрипт для управления миграциями базы данных
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command: str) -> bool:
    """Выполнить команду и вернуть результат"""
    try:
        result = subprocess.run(command.split(), capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {command}")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ {command}")
            print(f"Ошибка: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Ошибка выполнения команды '{command}': {e}")
        return False

def init_migrations():
    """Инициализировать миграции"""
    print("🚀 Инициализация миграций...")
    if run_command("alembic init migrations"):
        print("✅ Миграции инициализированы")
    else:
        print("❌ Ошибка инициализации миграций")

def create_migration(message: str):
    """Создать новую миграцию"""
    print(f"📝 Создание миграции: {message}")
    if run_command(f'alembic revision --autogenerate -m "{message}"'):
        print("✅ Миграция создана")
    else:
        print("❌ Ошибка создания миграции")

def upgrade_database():
    """Обновить базу данных до последней версии"""
    print("⬆️ Обновление базы данных...")
    if run_command("alembic upgrade head"):
        print("✅ База данных обновлена")
    else:
        print("❌ Ошибка обновления базы данных")

def downgrade_database(revision: str = "-1"):
    """Откатить базу данных"""
    print(f"⬇️ Откат базы данных к ревизии: {revision}")
    if run_command(f"alembic downgrade {revision}"):
        print("✅ База данных откачена")
    else:
        print("❌ Ошибка отката базы данных")

def show_migration_history():
    """Показать историю миграций"""
    print("📋 История миграций:")
    run_command("alembic history")

def show_current_revision():
    """Показать текущую ревизию"""
    print("📍 Текущая ревизия:")
    run_command("alembic current")

def show_pending_migrations():
    """Показать ожидающие миграции"""
    print("⏳ Ожидающие миграции:")
    run_command("alembic show")

def main():
    """Основная функция"""
    if len(sys.argv) < 2:
        print("""
🔧 Скрипт управления миграциями

Использование:
    python manage_migrations.py <команда> [аргументы]

Команды:
    init                    - Инициализировать миграции
    create <сообщение>      - Создать новую миграцию
    upgrade                 - Обновить базу данных
    downgrade [ревизия]     - Откатить базу данных
    history                 - Показать историю миграций
    current                 - Показать текущую ревизию
    pending                 - Показать ожидающие миграции

Примеры:
    python manage_migrations.py init
    python manage_migrations.py create "Add users table"
    python manage_migrations.py upgrade
    python manage_migrations.py downgrade
        """)
        return

    command = sys.argv[1]
    
    if command == "init":
        init_migrations()
    elif command == "create":
        if len(sys.argv) < 3:
            print("❌ Укажите сообщение для миграции")
            return
        message = sys.argv[2]
        create_migration(message)
    elif command == "upgrade":
        upgrade_database()
    elif command == "downgrade":
        revision = sys.argv[2] if len(sys.argv) > 2 else "-1"
        downgrade_database(revision)
    elif command == "history":
        show_migration_history()
    elif command == "current":
        show_current_revision()
    elif command == "pending":
        show_pending_migrations()
    else:
        print(f"❌ Неизвестная команда: {command}")

if __name__ == "__main__":
    main() 