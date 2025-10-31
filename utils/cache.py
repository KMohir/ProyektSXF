import time
from typing import Any, Optional
from utils.logger import logger

class SimpleCache:
    """Простой кэш в памяти с TTL"""
    
    def __init__(self, ttl: int = 300):
        self.cache = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Получить значение из кэша"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                logger.debug(f"Cache hit for key: {key}")
                return value
            else:
                logger.debug(f"Cache expired for key: {key}")
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """Сохранить значение в кэш"""
        self.cache[key] = (value, time.time())
        logger.debug(f"Cache set for key: {key}")
    
    def delete(self, key: str):
        """Удалить значение из кэша"""
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Cache deleted for key: {key}")
    
    def clear(self):
        """Очистить весь кэш"""
        self.cache.clear()
        logger.debug("Cache cleared")

# Глобальный экземпляр кэша
cache = SimpleCache()