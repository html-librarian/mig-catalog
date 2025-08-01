#!/usr/bin/env python3
"""
Профили тестирования для MIG Catalog API

Этот скрипт предоставляет различные профили тестирования для разных сценариев разработки.
"""

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List


class TestProfiles:
    """Профили тестирования для различных сценариев"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        
    def run_profile(self, profile_name: str) -> bool:
        """Запускает тесты по профилю"""
        profiles = {
            "quick": self.quick_profile,
            "development": self.development_profile,
            "ci": self.ci_profile,
            "security": self.security_profile,
            "performance": self.performance_profile,
            "full": self.full_profile,
            "smoke": self.smoke_profile,
            "regression": self.regression_profile,
        }
        
        if profile_name not in profiles:
            print(f"❌ Неизвестный профиль: {profile_name}")
            print(f"Доступные профили: {', '.join(profiles.keys())}")
            return False
        
        print(f"🚀 Запуск профиля: {profile_name}")
        print("=" * 50)
        
        start_time = time.time()
        success = profiles[profile_name]()
        end_time = time.time()
        
        duration = end_time - start_time
        print(f"\n⏱️  Время выполнения: {duration:.2f} секунд")
        
        if success:
            print("✅ Профиль выполнен успешно!")
        else:
            print("❌ Профиль завершился с ошибками!")
        
        return success
    
    def quick_profile(self) -> bool:
        """Быстрый профиль - только критические тесты"""
        print("🔍 Быстрый профиль - проверка критической функциональности")
        
        commands = [
            ["python3", "-m", "pytest", "tests/test_basic.py", "-v", "-m", "fast"],
            ["python3", "-m", "pytest", "tests/test_validators.py", "-v", "-m", "fast"],
        ]
        
        return self._run_commands(commands, "Быстрые тесты")
    
    def development_profile(self) -> bool:
        """Профиль разработки - основные тесты без медленных"""
        print("🛠️  Профиль разработки - основные тесты")
        
        commands = [
            ["python3", "-m", "pytest", "tests/test_basic.py", "-v"],
            ["python3", "-m", "pytest", "tests/test_validators.py", "-v"],
            ["python3", "-m", "pytest", "tests/test_auth.py", "-v"],
            ["python3", "-m", "pytest", "tests/test_services.py", "-v", "-m", "not slow"],
            ["python3", "-m", "flake8", "app/", "--max-line-length=79"],
        ]
        
        return self._run_commands(commands, "Тесты разработки")
    
    def ci_profile(self) -> bool:
        """CI профиль - полный набор тестов для CI/CD"""
        print("🔧 CI профиль - полный набор тестов")
        
        commands = [
            ["python3", "-m", "pytest", "tests/", "-v", "--cov=app", "--cov-report=term-missing"],
            ["bandit", "-r", "app/", "-f", "json"],
        ]
        
        return self._run_commands(commands, "CI тесты")
    
    def security_profile(self) -> bool:
        """Профиль безопасности - все тесты безопасности"""
        print("🛡️  Профиль безопасности - проверка безопасности")
        
        commands = [
            ["python3", "-m", "pytest", "tests/test_security.py", "-v"],
            ["python3", "-m", "pytest", "tests/test_auth.py", "-v"],
            ["bandit", "-r", "app/", "-f", "json"],
            ["pip-audit"],
        ]
        
        return self._run_commands(commands, "Тесты безопасности")
    
    def performance_profile(self) -> bool:
        """Профиль производительности - тесты производительности"""
        print("⚡ Профиль производительности - тесты производительности")
        
        commands = [
            ["python3", "-m", "pytest", "tests/test_services.py", "-v", "-m", "performance"],
            ["python3", "-m", "pytest", "tests/test_basic.py", "-v", "-m", "performance"],
        ]
        
        return self._run_commands(commands, "Тесты производительности")
    
    def full_profile(self) -> bool:
        """Полный профиль - все тесты и проверки"""
        print("🎯 Полный профиль - все тесты и проверки")
        
        commands = [
            ["python3", "-m", "pytest", "tests/", "-v", "--cov=app", "--cov-report=html"],
            ["python3", "-m", "flake8", "app/", "--max-line-length=79"],
            ["bandit", "-r", "app/", "-f", "json"],
            ["python3", "-m", "mypy", "app/", "--ignore-missing-imports"],
            ["pip-audit"],
            ["safety", "check"],
        ]
        
        return self._run_commands(commands, "Полные тесты")
    
    def smoke_profile(self) -> bool:
        """Smoke профиль - минимальные тесты для проверки работоспособности"""
        print("💨 Smoke профиль - проверка работоспособности")
        
        commands = [
            ["python3", "-m", "pytest", "tests/test_basic.py", "-v", "-m", "smoke"],
            ["curl", "-f", "http://localhost:8000/health"],
        ]
        
        return self._run_commands(commands, "Smoke тесты")
    
    def regression_profile(self) -> bool:
        """Регрессионный профиль - тесты для проверки регрессий"""
        print("🔄 Регрессионный профиль - проверка регрессий")
        
        commands = [
            ["python3", "-m", "pytest", "tests/test_services.py", "-v", "-m", "regression"],
            ["python3", "-m", "pytest", "tests/test_auth.py", "-v", "-m", "regression"],
            ["python3", "-m", "pytest", "tests/test_validators.py", "-v", "-m", "regression"],
        ]
        
        return self._run_commands(commands, "Регрессионные тесты")
    
    def _run_commands(self, commands: List[List[str]], description: str) -> bool:
        """Выполняет список команд"""
        success = True
        
        for i, command in enumerate(commands, 1):
            print(f"\n🔄 {description} ({i}/{len(commands)}): {' '.join(command)}")
            
            try:
                # Устанавливаем переменную окружения для тестов
                env = os.environ.copy()
                env["TESTING"] = "true"
                
                result = subprocess.run(
                    command,
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=300,
                    env=env
                )
                
                if result.returncode == 0:
                    print(f"✅ Команда {i} выполнена успешно")
                    if result.stdout:
                        print(result.stdout)
                else:
                    print(f"❌ Команда {i} завершилась с ошибкой")
                    if result.stderr:
                        print(result.stderr)
                    success = False
                    
            except subprocess.TimeoutExpired:
                print(f"⏰ Команда {i} превысила таймаут")
                success = False
            except Exception as e:
                print(f"💥 Команда {i} завершилась с исключением: {e}")
                success = False
        
        return success


def main():
    """Главная функция"""
    if len(sys.argv) < 2:
        print("Использование: python test_profiles.py <профиль>")
        print("\nДоступные профили:")
        print("  quick        - Быстрые тесты")
        print("  development  - Профиль разработки")
        print("  ci           - CI/CD профиль")
        print("  security     - Профиль безопасности")
        print("  performance  - Профиль производительности")
        print("  full         - Полный профиль")
        print("  smoke        - Smoke тесты")
        print("  regression   - Регрессионные тесты")
        sys.exit(1)
    
    profile_name = sys.argv[1]
    runner = TestProfiles()
    
    success = runner.run_profile(profile_name)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 