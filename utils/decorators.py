import asyncio
from functools import wraps
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from utils.logger import logger
from config import MAX_RETRIES, RETRY_DELAY

def async_retry(max_attempts=MAX_RETRIES):
    """Декоратор для повторных попыток выполнения асинхронных функций"""
    def decorator(func):
        @wraps(func)
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=RETRY_DELAY, max=60),
            retry=retry_if_exception_type((ConnectionError, TimeoutError)),
            reraise=True
        )
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                raise
        return wrapper
    return decorator

def log_execution(func):
    """Декоратор для логирования выполнения функций"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger.info(f"Executing {func.__name__}")
        try:
            result = await func(*args, **kwargs)
            logger.info(f"Successfully executed {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"Error executing {func.__name__}: {e}")
            raise
    return wrapper