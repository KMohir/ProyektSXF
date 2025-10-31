import logging
import sys
from logging.handlers import RotatingFileHandler
from config import LOG_LEVEL, LOG_FILE

def setup_logger(name: str = __name__) -> logging.Logger:
    """Настройка логгера с ротацией файлов"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Консольный обработчик
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Файловый обработчик с ротацией
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Добавляем обработчики
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Глобальный логгер
logger = setup_logger('bot')