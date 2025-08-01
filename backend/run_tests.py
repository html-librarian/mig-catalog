#!/usr/bin/env python3
"""
Централизованный скрипт для запуска тестов MIG Catalog API

Использование:
    python run_tests.py                    # Запуск всех тестов
    python run_tests.py --fast            # Быстрые тесты
    python run_tests.py --security        # Только тесты безопасности
    python run_tests.py --basic           # Только базовые тесты
    python run_tests.py --services        # Только тесты сервисов
    python run_tests.py --auth            # Только тесты аутентификации
    python run_tests.py --validators      # Только тесты валидации
    python run_tests.py --coverage        # Тесты с покрытием
    python run_tests.py --verbose         # Подробный вывод
    python run_tests.py --parallel        # Параллельное выполнение
    python run_tests.py --help            # Справка
"""

import sys
import subprocess
import argparse
import os
from pathlib import Path
from typing import List, Optional


class TestRunner:
    """Класс для управления тестированием"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.tests_dir = self.project_root / "tests"
        self.coverage_dir = self.project_root / "htmlcov"
        
    def run_command(self, command: List[str], description: str) -> bool:
        """Выполняет команду и возвращает результат"""
        print(f"\n🔄 {description}...")
        print(f"Команда: {' '.join(command)}")
        
        try:
            # Устанавливаем переменную окружения для тестов
            env = os.environ.copy()
            env["TESTING"] = "true"
            
            result = subprocess.run(
                command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300,  # 5 минут таймаут
                env=env
            )
            
            if result.returncode == 0:
                print(f"✅ {description} - УСПЕШНО")
                if result.stdout:
                    print(result.stdout)
                return True
            else:
                print(f"❌ {description} - ОШИБКА")
                if result.stderr:
                    print(result.stderr)
                if result.stdout:
                    print(result.stdout)
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {description} - ТАЙМАУТ")
            return False
        except Exception as e:
            print(f"💥 {description} - ИСКЛЮЧЕНИЕ: {e}")
            return False
    
    def install_dependencies(self) -> bool:
        """Устанавливает зависимости для тестирования"""
        return self.run_command(
            ["pip", "install", "-r", "requirements.txt"],
            "Установка зависимостей"
        )
    
    def run_basic_tests(self) -> bool:
        """Запускает базовые тесты"""
        return self.run_command(
            ["python3", "-m", "pytest", "tests/test_basic.py", "-v"],
            "Базовые тесты"
        )
    
    def run_auth_tests(self) -> bool:
        """Запускает тесты аутентификации"""
        return self.run_command(
            ["python3", "-m", "pytest", "tests/test_auth.py", "-v"],
            "Тесты аутентификации"
        )
    
    def run_security_tests(self) -> bool:
        """Запускает тесты безопасности"""
        return self.run_command(
            ["python3", "-m", "pytest", "tests/test_security.py", "-v"],
            "Тесты безопасности"
        )
    
    def run_validators_tests(self) -> bool:
        """Запускает тесты валидации"""
        return self.run_command(
            ["python3", "-m", "pytest", "tests/test_validators.py", "-v"],
            "Тесты валидации"
        )
    
    def run_services_tests(self) -> bool:
        """Запускает тесты сервисов"""
        return self.run_command(
            ["python3", "-m", "pytest", "tests/test_services.py", "-v"],
            "Тесты сервисов"
        )
    
    def run_fast_tests(self) -> bool:
        """Запускает быстрые тесты (без интеграционных)"""
        return self.run_command(
            ["python3", "-m", "pytest", "tests/test_basic.py", "tests/test_validators.py", "-v"],
            "Быстрые тесты"
        )
    
    def run_all_tests(self, parallel: bool = False) -> bool:
        """Запускает все тесты"""
        cmd = ["python3", "-m", "pytest", "tests/", "-v"]
        if parallel:
            cmd.extend(["-n", "auto"])
        
        return self.run_command(cmd, "Все тесты")
    
    def run_tests_with_coverage(self) -> bool:
        """Запускает тесты с покрытием кода"""
        return self.run_command(
            [
                "python3", "-m", "pytest", "tests/", 
                "--cov=app", 
                "--cov-report=html",
                "--cov-report=term-missing",
                "-v"
            ],
            "Тесты с покрытием кода"
        )
    
    def run_linting(self) -> bool:
        """Запускает проверку кода"""
        return self.run_command(
            ["python3", "-m", "flake8", "app/", "--max-line-length=79"],
            "Проверка стиля кода"
        )
    
    def run_security_scan(self) -> bool:
        """Запускает сканирование безопасности"""
        return self.run_command(
            ["bandit", "-r", "app/", "-f", "json"],
            "Сканирование безопасности"
        )
    
    def run_type_checking(self) -> bool:
        """Запускает проверку типов"""
        return self.run_command(
            ["python3", "-m", "mypy", "app/"],
            "Проверка типов"
        )
    
    def cleanup_coverage(self):
        """Очищает файлы покрытия"""
        if self.coverage_dir.exists():
            import shutil
            shutil.rmtree(self.coverage_dir)
            print("🧹 Очищены файлы покрытия")
    
    def show_coverage_report(self):
        """Показывает отчет о покрытии"""
        coverage_file = self.coverage_dir / "index.html"
        if coverage_file.exists():
            print(f"\n📊 Отчет о покрытии: {coverage_file}")
            print("Откройте файл в браузере для просмотра")
        else:
            print("📊 Отчет о покрытии не найден")
    
    def run_test_suite(self, args) -> bool:
        """Запускает выбранный набор тестов"""
        success = True
        
        # Устанавливаем зависимости если нужно
        if args.install_deps:
            success &= self.install_dependencies()
        
        # Очищаем покрытие если нужно
        if args.coverage:
            self.cleanup_coverage()
        
        # Запускаем выбранные тесты
        if args.fast:
            success &= self.run_fast_tests()
        elif args.basic:
            success &= self.run_basic_tests()
        elif args.auth:
            success &= self.run_auth_tests()
        elif args.security:
            success &= self.run_security_tests()
        elif args.validators:
            success &= self.run_validators_tests()
        elif args.services:
            success &= self.run_services_tests()
        elif args.coverage:
            success &= self.run_tests_with_coverage()
            if success:
                self.show_coverage_report()
        else:
            # По умолчанию запускаем все тесты
            success &= self.run_all_tests(args.parallel)
        
        # Дополнительные проверки
        if args.lint:
            success &= self.run_linting()
        
        if args.security_scan:
            success &= self.run_security_scan()
        
        if args.type_check:
            success &= self.run_type_checking()
        
        return success


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description="Централизованный запуск тестов MIG Catalog API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python run_tests.py                    # Все тесты
  python run_tests.py --fast            # Быстрые тесты
  python run_tests.py --security        # Тесты безопасности
  python run_tests.py --coverage        # Тесты с покрытием
  python run_tests.py --parallel        # Параллельное выполнение
  python run_tests.py --lint            # Проверка стиля кода
        """
    )
    
    # Группа тестов
    test_group = parser.add_mutually_exclusive_group()
    test_group.add_argument("--fast", action="store_true", help="Быстрые тесты")
    test_group.add_argument("--basic", action="store_true", help="Базовые тесты")
    test_group.add_argument("--auth", action="store_true", help="Тесты аутентификации")
    test_group.add_argument("--security", action="store_true", help="Тесты безопасности")
    test_group.add_argument("--validators", action="store_true", help="Тесты валидации")
    test_group.add_argument("--services", action="store_true", help="Тесты сервисов")
    test_group.add_argument("--coverage", action="store_true", help="Тесты с покрытием кода")
    
    # Дополнительные опции
    parser.add_argument("--parallel", action="store_true", help="Параллельное выполнение")
    parser.add_argument("--verbose", "-v", action="store_true", help="Подробный вывод")
    parser.add_argument("--install-deps", action="store_true", help="Установить зависимости")
    parser.add_argument("--lint", action="store_true", help="Проверка стиля кода")
    parser.add_argument("--security-scan", action="store_true", help="Сканирование безопасности")
    parser.add_argument("--type-check", action="store_true", help="Проверка типов")
    
    args = parser.parse_args()
    
    # Создаем runner и запускаем тесты
    runner = TestRunner()
    
    print("🚀 Запуск тестов MIG Catalog API")
    print("=" * 50)
    
    success = runner.run_test_suite(args)
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Все тесты прошли успешно!")
        sys.exit(0)
    else:
        print("💥 Некоторые тесты не прошли!")
        sys.exit(1)


if __name__ == "__main__":
    main() 