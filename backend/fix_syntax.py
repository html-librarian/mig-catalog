#!/usr/bin/env python3
"""
Скрипт для автоматического исправления синтаксических ошибок
"""

import re
from pathlib import Path


def fix_syntax_errors(file_path):
    """Исправляет синтаксические ошибки в файле"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Исправляем все синтаксические ошибки
    fixed_content = content
    
    # Исправляем += ошибки
    fixed_content = re.sub(r'(\w+)\s+\+\s*=\s*', r'\1 += ', fixed_content)
    
    # Исправляем *= ошибки  
    fixed_content = re.sub(r'(\w+)\s+\*\s*=\s*', r'\1 *= ', fixed_content)
    
    # Исправляем -= ошибки
    fixed_content = re.sub(r'(\w+)\s+-\s*=\s*', r'\1 -= ', fixed_content)
    
    # Исправляем /= ошибки
    fixed_content = re.sub(r'(\w+)\s+/\s*=\s*', r'\1 /= ', fixed_content)
    
    # Исправляем //= ошибки
    fixed_content = re.sub(r'(\w+)\s+//\s*=\s*', r'\1 //= ', fixed_content)
    
    # Исправляем %= ошибки
    fixed_content = re.sub(r'(\w+)\s+%\s*=\s*', r'\1 %= ', fixed_content)
    
    # Исправляем **= ошибки
    fixed_content = re.sub(r'(\w+)\s+\*\*\s*=\s*', r'\1 **= ', fixed_content)
    
    # Исправляем &= ошибки
    fixed_content = re.sub(r'(\w+)\s+&\s*=\s*', r'\1 &= ', fixed_content)
    
    # Исправляем |= ошибки
    fixed_content = re.sub(r'(\w+)\s+\|\s*=\s*', r'\1 |= ', fixed_content)
    
    # Исправляем ^= ошибки
    fixed_content = re.sub(r'(\w+)\s+\^\s*=\s*', r'\1 ^= ', fixed_content)
    
    # Исправляем <<= ошибки
    fixed_content = re.sub(r'(\w+)\s+<<\s*=\s*', r'\1 <<= ', fixed_content)
    
    # Исправляем >>= ошибки
    fixed_content = re.sub(r'(\w+)\s+>>\s*=\s*', r'\1 >>= ', fixed_content)
    
    # Записываем исправленный контент
    if fixed_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"✅ Исправлен: {file_path}")
        return True
    
    return False


def main():
    """Основная функция"""
    app_dir = Path("app")
    
    # Находим все Python файлы
    python_files = list(app_dir.rglob("*.py"))
    
    print(f"🔧 Исправляем синтаксические ошибки в {len(python_files)} файлах...")
    
    fixed_count = 0
    for file_path in python_files:
        try:
            if fix_syntax_errors(file_path):
                fixed_count += 1
        except Exception as e:
            print(f"❌ Ошибка в {file_path}: {e}")
    
    print(f"✅ Исправлено {fixed_count} файлов!")
    
    # Проверяем, что все импорты работают
    print("\n🔍 Проверяем импорты...")
    try:
        import app.core.exceptions
        import app.db.session
        import app.orders.services.order_service
        print("✅ Все основные модули импортируются успешно!")
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")


if __name__ == "__main__":
    main() 