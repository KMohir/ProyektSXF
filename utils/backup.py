"""
Утилита для создания резервных копий базы данных
"""
import asyncio
import os
import sys
from datetime import datetime

# Добавляем родительскую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import db
from utils.logger import logger

async def backup_database():
    """Создание резервной копии базы данных"""
    try:
        await db.create_pool()
        
        # Создаем директорию для бэкапов
        backup_dir = "backups"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Имя файла с датой и временем
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"backup_{timestamp}.sql")
        
        # Экспорт данных
        async with db.pool.acquire() as conn:
            # Экспорт пользователей
            users = await conn.fetch("SELECT * FROM users")
            tasks = await conn.fetch("SELECT * FROM tasks")
            logs = await conn.fetch("SELECT * FROM action_logs")
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(f"-- Backup created at {datetime.now()}\n\n")
                
                f.write(f"-- Users: {len(users)}\n")
                f.write(f"-- Tasks: {len(tasks)}\n")
                f.write(f"-- Logs: {len(logs)}\n\n")
                
                # Здесь можно добавить SQL команды для восстановления
        
        logger.info(f"✅ Backup created: {backup_file}")
        logger.info(f"Users: {len(users)}, Tasks: {len(tasks)}, Logs: {len(logs)}")
        
        await db.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Backup Error: {e}")
        return False

if __name__ == '__main__':
    asyncio.run(backup_database())