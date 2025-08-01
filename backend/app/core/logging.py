import logging
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Создаем папку для логов (абсолютный путь)
log_dir  =  Path(__file__).parent.parent.parent / "logs"
log_dir.mkdir(exist_ok = True)

# Настройки логирования
LOG_LEVEL  =  os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT  =  "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE  =  log_dir / f"mig_catalog_{datetime.now().strftime('%Y%m%d')}.log"

def setup_logging():
    """Настройка логирования"""
    # Настраиваем корневой логгер
    logging.basicConfig(
        level = getattr(logging, LOG_LEVEL),
        format = LOG_FORMAT,
        handlers = [
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )

    # Создаем логгер для приложения
    logger  =  logging.getLogger("mig_catalog")
    logger.setLevel(getattr(logging, LOG_LEVEL))

    # Настраиваем логгеры для сторонних библиотек
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

    return logger

def get_logger(name: str  =  "mig_catalog"):
    """Получить логгер"""
    return logging.getLogger(name)

# Инициализируем логирование
logger  =  setup_logging()
