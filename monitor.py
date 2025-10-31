"""
Скрипт мониторинга бота
Отправляет уведомления администраторам о состоянии системы
"""
import asyncio
import psutil
import os
from datetime import datetime
from aiogram import Bot
from config import BOT_TOKEN, ADMIN_IDS
from db import db
from utils.logger import logger

bot = Bot(token=BOT_TOKEN)

async def get_system_info():
    """Получение информации о системе"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        'cpu': cpu_percent,
        'memory_percent': memory.percent,
        'memory_used': memory.used / (1024**3),  # GB
        'memory_total': memory.total / (1024**3),  # GB
        'disk_percent': disk.percent,
        'disk_used': disk.used / (1024**3),  # GB
        'disk_total': disk.total / (1024**3),  # GB
    }

async def get_bot_stats():
    """Получение статистики бота"""
    try:
        await db.create_pool()
        stats = await db.get_statistics()
        await db.close()
        return stats
    except Exception as e:
        logger.error(f"Error getting bot stats: {e}")
        return {}

async def send_monitoring_report():
    """Отправка отчета о мониторинге"""
    try:
        system_info = await get_system_info()
        bot_stats = await get_bot_stats()
        
        report = (
            f"📊 <b>Отчет о состоянии системы</b>\n"
            f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            f"<b>💻 Система:</b>\n"
            f"CPU: {system_info['cpu']:.1f}%\n"
            f"RAM: {system_info['memory_used']:.1f}/{system_info['memory_total']:.1f} GB ({system_info['memory_percent']:.1f}%)\n"
            f"Disk: {system_info['disk_used']:.1f}/{system_info['disk_total']:.1f} GB ({system_info['disk_percent']:.1f}%)\n\n"
            
            f"<b>🤖 Бот:</b>\n"
            f"Пользователей: {bot_stats.get('total_users', 0)}\n"
            f"Активных (7д): {bot_stats.get('active_users', 0)}\n"
            f"Задач всего: {bot_stats.get('total_tasks', 0)}\n"
            f"В ожидании: {bot_stats.get('pending_tasks', 0)}\n"
            f"Одобрено: {bot_stats.get('approved_tasks', 0)}\n"
        )
        
        # Предупреждения
        warnings = []
        if system_info['cpu'] > 80:
            warnings.append("⚠️ Высокая загрузка CPU!")
        if system_info['memory_percent'] > 80:
            warnings.append("⚠️ Высокое использование RAM!")
        if system_info['disk_percent'] > 80:
            warnings.append("⚠️ Мало места на диске!")
        
        if warnings:
            report += "\n<b>⚠️ Предупреждения:</b>\n" + "\n".join(warnings)
        
        # Отправляем отчет администраторам
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(admin_id, report, parse_mode='HTML')
            except Exception as e:
                logger.error(f"Error sending report to admin {admin_id}: {e}")
        
        logger.info("Monitoring report sent successfully")
        
    except Exception as e:
        logger.error(f"Error in monitoring: {e}")
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(send_monitoring_report())