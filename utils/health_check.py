"""
Утилита для проверки здоровья системы
"""
import asyncio
import sys
import os

# Добавляем родительскую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import db
from sheets import sheets_manager
from utils.logger import logger

async def check_database():
    """Проверка подключения к базе данных"""
    try:
        await db.create_pool()
        stats = await db.get_statistics()
        logger.info(f"✅ Database OK - {stats.get('total_users', 0)} users")
        await db.close()
        return True
    except Exception as e:
        logger.error(f"❌ Database Error: {e}")
        return False

async def check_google_sheets():
    """Проверка подключения к Google Sheets"""
    try:
        await sheets_manager.initialize()
        projects = await sheets_manager.get_project_names()
        logger.info(f"✅ Google Sheets OK - {len(projects)} projects")
        return True
    except Exception as e:
        logger.error(f"❌ Google Sheets Error: {e}")
        return False

async def main():
    """Главная функция проверки"""
    logger.info("=" * 50)
    logger.info("Health Check Started")
    logger.info("=" * 50)
    
    db_ok = await check_database()
    sheets_ok = await check_google_sheets()
    
    logger.info("=" * 50)
    if db_ok and sheets_ok:
        logger.info("✅ All systems operational")
        sys.exit(0)
    else:
        logger.error("❌ Some systems are down")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())