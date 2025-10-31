#!/usr/bin/env python3
"""
Скрипт для запуска бота с автоматическим перезапуском при ошибках
"""
import asyncio
import sys
from bot import dp, on_startup, on_shutdown
from aiogram.utils import executor
from utils.logger import logger

def main():
    """Главная функция запуска"""
    try:
        logger.info("=" * 50)
        logger.info("Starting Telegram Task Manager Bot")
        logger.info("=" * 50)
        
        executor.start_polling(
            dp,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            timeout=60,
            relax=0.1,
            fast=True
        )
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()