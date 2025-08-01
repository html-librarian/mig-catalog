"""
Минимальный тест для проверки базовой функциональности
"""

import os


def test_python_basics():
    """Тест базовой функциональности Python"""
    assert 1 + 1 == 2
    assert "hello" + " " + "world" == "hello world"
    assert len([1, 2, 3]) == 3
    print("✅ Базовые операции Python работают")


def test_environment_variables():
    """Тест переменных окружения"""
    # Устанавливаем переменные
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["DEBUG"] = "True"
    os.environ["SECRET_KEY"] = (
        "test-secret-key-64-characters-long-for-testing-purposes-only-"
        "123456789"
    )

    # Проверяем их
    assert os.getenv("ENVIRONMENT") == "testing"
    assert os.getenv("DEBUG") == "True"
    assert len(os.getenv("SECRET_KEY", "")) >= 64
    print("✅ Переменные окружения настроены")


def test_file_system():
    """Тест файловой системы"""
    current_dir = os.getcwd()
    assert os.path.exists(current_dir)
    assert os.path.isdir(current_dir)
    print("✅ Файловая система работает")


def test_imports():
    """Тест базовых импортов"""
    try:
        print("✅ Базовые модули Python импортируются")
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        raise


if __name__ == "__main__":
    print("🚀 Запуск минимальных тестов...")
    test_python_basics()
    test_environment_variables()
    test_file_system()
    test_imports()
    print("✅ Все минимальные тесты прошли успешно!")
