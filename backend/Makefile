# Makefile для MIG Catalog API
# Удобные команды для разработки и тестирования

.PHONY: help install test test-fast test-basic test-auth test-security test-validators test-services test-coverage lint security-scan type-check clean run dev docker-build docker-run

# Цвета для вывода
GREEN = \033[0;32m
RED = \033[0;31m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

# Переменные
PYTHON = python3
PIP = pip3
PYTEST = pytest
COVERAGE = coverage
LINT = flake8
SECURITY = bandit
TYPE_CHECK = mypy

help: ## Показать справку
	@echo "$(BLUE)MIG Catalog API - Команды разработки$(NC)"
	@echo ""
	@echo "$(GREEN)Установка и настройка:$(NC)"
	@echo "  make install          - Установить зависимости"
	@echo "  make clean            - Очистить кэш и временные файлы"
	@echo ""
	@echo "$(GREEN)Тестирование:$(NC)"
	@echo "  make test             - Запустить все тесты"
	@echo "  make test-fast        - Быстрые тесты"
	@echo "  make test-basic       - Базовые тесты"
	@echo "  make test-auth        - Тесты аутентификации"
	@echo "  make test-security    - Тесты безопасности"
	@echo "  make test-validators  - Тесты валидации"
	@echo "  make test-services    - Тесты сервисов"
	@echo "  make test-coverage    - Тесты с покрытием кода"
	@echo ""
	@echo "$(GREEN)Проверка качества кода:$(NC)"
	@echo "  make lint             - Проверка стиля кода"
	@echo "  make security-scan    - Сканирование безопасности"
	@echo "  make type-check       - Проверка типов"
	@echo "  make quality          - Все проверки качества"
	@echo ""
	@echo "$(GREEN)Запуск приложения:$(NC)"
	@echo "  make run              - Запустить приложение"
	@echo "  make dev              - Запустить в режиме разработки"
	@echo "  make docker-build     - Собрать Docker образ"
	@echo "  make docker-run       - Запустить в Docker"
	@echo ""

install: ## Установить зависимости
	@echo "$(BLUE)Установка зависимостей...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)Зависимости установлены!$(NC)"

clean: ## Очистить кэш и временные файлы
	@echo "$(BLUE)Очистка временных файлов...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	@echo "$(GREEN)Очистка завершена!$(NC)"

test: ## Запустить все тесты
	@echo "$(BLUE)Запуск всех тестов...$(NC)"
	$(PYTHON) run_tests.py

test-fast: ## Быстрые тесты
	@echo "$(BLUE)Запуск быстрых тестов...$(NC)"
	$(PYTHON) run_tests.py --fast

test-basic: ## Базовые тесты
	@echo "$(BLUE)Запуск базовых тестов...$(NC)"
	$(PYTHON) run_tests.py --basic

test-auth: ## Тесты аутентификации
	@echo "$(BLUE)Запуск тестов аутентификации...$(NC)"
	$(PYTHON) run_tests.py --auth

test-security: ## Тесты безопасности
	@echo "$(BLUE)Запуск тестов безопасности...$(NC)"
	$(PYTHON) run_tests.py --security

test-validators: ## Тесты валидации
	@echo "$(BLUE)Запуск тестов валидации...$(NC)"
	$(PYTHON) run_tests.py --validators

test-services: ## Тесты сервисов
	@echo "$(BLUE)Запуск тестов сервисов...$(NC)"
	$(PYTHON) run_tests.py --services

test-coverage: ## Тесты с покрытием кода
	@echo "$(BLUE)Запуск тестов с покрытием...$(NC)"
	$(PYTHON) run_tests.py --coverage

lint: ## Проверка стиля кода
	@echo "$(BLUE)Проверка стиля кода...$(NC)"
	$(LINT) app/ --max-line-length=79 --exclude=__pycache__,.git,*.egg
	@echo "$(GREEN)Проверка стиля завершена!$(NC)"

security-scan: ## Сканирование безопасности
	@echo "$(BLUE)Сканирование безопасности...$(NC)"
	$(SECURITY) -r app/ -f json -o security-report.json || true
	@echo "$(GREEN)Сканирование безопасности завершено!$(NC)"

type-check: ## Проверка типов
	@echo "$(BLUE)Проверка типов...$(NC)"
	$(TYPE_CHECK) app/ --ignore-missing-imports || true
	@echo "$(GREEN)Проверка типов завершена!$(NC)"

quality: lint security-scan type-check ## Все проверки качества кода
	@echo "$(GREEN)Все проверки качества завершены!$(NC)"

run: ## Запустить приложение
	@echo "$(BLUE)Запуск приложения...$(NC)"
	uvicorn app.main:app --host 0.0.0.0 --port 8000

dev: ## Запустить в режиме разработки
	@echo "$(BLUE)Запуск в режиме разработки...$(NC)"
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

docker-build: ## Собрать Docker образ
	@echo "$(BLUE)Сборка Docker образа...$(NC)"
	docker build -t mig-catalog-api .
	@echo "$(GREEN)Docker образ собран!$(NC)"

docker-run: ## Запустить в Docker
	@echo "$(BLUE)Запуск в Docker...$(NC)"
	docker run -p 8000:8000 --env-file .env mig-catalog-api

docker-test: ## Запустить тесты в Docker
	@echo "$(BLUE)Запуск тестов в Docker...$(NC)"
	docker run --rm -v $(PWD):/app -w /app python:3.9-slim bash -c \
		"pip install -r requirements.txt && python run_tests.py"

# Команды для CI/CD
ci-test: install test-coverage lint security-scan type-check ## Полный набор тестов для CI
	@echo "$(GREEN)CI тесты завершены!$(NC)"

# Команды для мониторинга
health: ## Проверить здоровье приложения
	@echo "$(BLUE)Проверка здоровья приложения...$(NC)"
	curl -f http://localhost:8000/health || echo "$(RED)Приложение недоступно$(NC)"

metrics: ## Получить метрики
	@echo "$(BLUE)Получение метрик...$(NC)"
	curl -f http://localhost:8000/metrics || echo "$(RED)Метрики недоступны$(NC)"

# Команды для базы данных
db-migrate: ## Запустить миграции
	@echo "$(BLUE)Запуск миграций...$(NC)"
	alembic upgrade head

db-rollback: ## Откатить миграции
	@echo "$(BLUE)Откат миграций...$(NC)"
	alembic downgrade -1

db-reset: ## Сбросить базу данных
	@echo "$(RED)ВНИМАНИЕ: Это удалит все данные!$(NC)"
	@read -p "Продолжить? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	alembic downgrade base
	alembic upgrade head

# Команды для разработки
format: ## Форматировать код
	@echo "$(BLUE)Форматирование кода...$(NC)"
	black app/ tests/
	isort app/ tests/

check-format: ## Проверить форматирование
	@echo "$(BLUE)Проверка форматирования...$(NC)"
	black --check app/ tests/
	isort --check-only app/ tests/

# Команды для документации
docs: ## Генерировать документацию
	@echo "$(BLUE)Генерация документации...$(NC)"
	pydoc-markdown --render-toc --output-dir docs/ app/

# Команды для профилирования
profile: ## Профилирование производительности
	@echo "$(BLUE)Профилирование...$(NC)"
	python -m cProfile -o profile.stats -m uvicorn app.main:app --host 0.0.0.0 --port 8000

analyze-profile: ## Анализ профиля
	@echo "$(BLUE)Анализ профиля...$(NC)"
	python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(20)"

# Команды для безопасности
audit: ## Аудит безопасности
	@echo "$(BLUE)Аудит безопасности...$(NC)"
	pip-audit
	safety check

# Команды для бэкапов
backup: ## Создать бэкап
	@echo "$(BLUE)Создание бэкапа...$(NC)"
	tar -czf backup-$(shell date +%Y%m%d-%H%M%S).tar.gz app/ tests/ requirements.txt

# Команды для мониторинга логов
logs: ## Показать логи
	@echo "$(BLUE)Показать логи...$(NC)"
	tail -f logs/app.log

logs-error: ## Показать ошибки в логах
	@echo "$(BLUE)Показать ошибки в логах...$(NC)"
	grep -i error logs/app.log || echo "Ошибок не найдено"

# Команды для тестирования производительности
benchmark: ## Тестирование производительности
	@echo "$(BLUE)Тестирование производительности...$(NC)"
	ab -n 1000 -c 10 http://localhost:8000/health

# Команды для обновления зависимостей
update-deps: ## Обновить зависимости
	@echo "$(BLUE)Обновление зависимостей...$(NC)"
	pip install --upgrade pip
	pip install --upgrade -r requirements.txt

check-deps: ## Проверить устаревшие зависимости
	@echo "$(BLUE)Проверка устаревших зависимостей...$(NC)"
	pip list --outdated

# Команды для очистки Docker
docker-clean: ## Очистить Docker
	@echo "$(BLUE)Очистка Docker...$(NC)"
	docker system prune -f
	docker image prune -f
	docker container prune -f

# Команды для развертывания
deploy-staging: ## Развернуть на staging
	@echo "$(BLUE)Развертывание на staging...$(NC)"
	# Добавьте команды для развертывания на staging

deploy-production: ## Развернуть на production
	@echo "$(RED)ВНИМАНИЕ: Развертывание на production!$(NC)"
	@read -p "Продолжить? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	# Добавьте команды для развертывания на production 