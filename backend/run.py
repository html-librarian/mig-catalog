#!/usr/bin/env python3
"""
Скрипт для запуска FastAPI приложения
"""

import uvicorn
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

if __name__ == "__main__":
    # Получаем настройки из переменных окружения или используем значения по умолчанию
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    print(f"🚀 Запуск MIG Catalog API на {host}:{port}")
    print(f"📚 Документация: http://{host}:{port}/docs")
    print(f"🔍 ReDoc: http://{host}:{port}/redoc")
    print(f"💚 Health check: http://{host}:{port}/health")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level=log_level,
        access_log=True
    ) 