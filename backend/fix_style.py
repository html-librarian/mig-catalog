#!/usr/bin/env python3
"""
Скрипт для автоматического исправления ошибок стиля кода
"""

import re
from pathlib import Path


def fix_file(file_path):
    """Исправляет ошибки стиля в файле"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Исправляем trailing whitespace
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Убираем trailing whitespace
        line = line.rstrip()
        fixed_lines.append(line)
    
    # Добавляем newline в конце файла
    if fixed_lines and fixed_lines[-1] != '':
        fixed_lines.append('')
    
    # Объединяем строки
    fixed_content = '\n'.join(fixed_lines)
    
    # Исправляем длинные строки (разбиваем на несколько строк)
    fixed_content = re.sub(
        r'([^=<>!])=([^=])',
        r'\1 = \2',
        fixed_content
    )
    
    # Записываем исправленный контент
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"✅ Исправлен: {file_path}")


def main():
    """Основная функция"""
    app_dir = Path("app")
    
    # Находим все Python файлы
    python_files = list(app_dir.rglob("*.py"))
    
    print(f"🔧 Исправляем стиль в {len(python_files)} файлах...")
    
    for file_path in python_files:
        try:
            fix_file(file_path)
        except Exception as e:
            print(f"❌ Ошибка в {file_path}: {e}")
    
    print("✅ Исправление стиля завершено!")


if __name__ == "__main__":
    main() 