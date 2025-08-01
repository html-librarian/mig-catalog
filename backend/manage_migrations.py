#!/usr/bin/env python3
"""
Скрипт для управления миграциями базы данных
Использует Alembic для управления миграциями
"""

import argparse
import subprocess
from pathlib import Path


def run_alembic_command(args):
    """Запустить команду Alembic"""
    try:
        result = subprocess.run(
            ["alembic"] + args,
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            check=True,
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Ошибка выполнения команды Alembic: {e}")
        print(f"Вывод ошибки: {e.stderr}")
        return False
    except FileNotFoundError:
        print("Ошибка: Alembic не найден. Убедитесь, что он установлен.")
        return False


def show_status():
    """Показать статус миграций"""
    print("📊 Статус миграций:")
    run_alembic_command(["current"])
    print("\n📋 История миграций:")
    run_alembic_command(["history"])


def upgrade_migrations(revision="head"):
    """Обновить миграции"""
    print(f"🔄 Обновление миграций до {revision}...")
    if run_alembic_command(["upgrade", revision]):
        print("✅ Миграции успешно обновлены!")
        show_status()


def downgrade_migrations(revision="-1"):
    """Откатить миграции"""
    print(f"⏪ Откат миграций на {revision}...")
    if run_alembic_command(["downgrade", revision]):
        print("✅ Миграции успешно откачены!")
        show_status()


def reset_database():
    """Сбросить базу данных"""
    print("⚠️  ВНИМАНИЕ: Это удалит все данные!")
    confirm = input("Продолжить? (y/N): ")
    if confirm.lower() != "y":
        print("❌ Операция отменена.")
        return

    print("🔄 Сброс базы данных...")
    if run_alembic_command(["downgrade", "base"]):
        print("✅ База данных сброшена!")
        print("🔄 Применение миграций...")
        if run_alembic_command(["upgrade", "head"]):
            print("✅ База данных восстановлена!")
            show_status()


def create_migration(message):
    """Создать новую миграцию"""
    print(f"📝 Создание новой миграции: {message}")
    if run_alembic_command(["revision", "--autogenerate", "-m", message]):
        print("✅ Миграция создана!")
        show_status()


def main():
    parser = argparse.ArgumentParser(
        description="Управление миграциями базы данных",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python manage_migrations.py status          # Показать статус
  python manage_migrations.py upgrade        # Обновить до последней версии
  python manage_migrations.py upgrade 001    # Обновить до конкретной версии
  python manage_migrations.py downgrade      # Откатить на одну версию
  python manage_migrations.py downgrade base # Откатить до начала
  python manage_migrations.py reset          # Сбросить базу данных
  python manage_migrations.py create "Add users table"  # Создать миграцию
        """,
    )

    parser.add_argument(
        "action",
        choices=["status", "upgrade", "downgrade", "reset", "create"],
        help="Действие для выполнения",
    )

    parser.add_argument(
        "revision",
        nargs="?",
        default="head",
        help="Ревизия для upgrade/downgrade или сообщение для create",
    )

    args = parser.parse_args()

    if args.action == "status":
        show_status()
    elif args.action == "upgrade":
        upgrade_migrations(args.revision)
    elif args.action == "downgrade":
        downgrade_migrations(args.revision)
    elif args.action == "reset":
        reset_database()
    elif args.action == "create":
        create_migration(args.revision)


if __name__ == "__main__":
    main()
