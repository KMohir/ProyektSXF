import os
import gspread_asyncio
from google.oauth2.service_account import Credentials
from typing import List, Optional
from utils.logger import logger
from utils.decorators import async_retry
from utils.cache import cache
from config import GOOGLE_SHEETS_CREDENTIALS_FILE, GOOGLE_SHEETS_URL, CACHE_TTL

class GoogleSheetsManager:
    def __init__(self):
        self.agcm = None
        self.spreadsheet = None
        self.cache_ttl = CACHE_TTL
    
    @async_retry(max_attempts=5)
    async def initialize(self):
        """Инициализация подключения к Google Sheets"""
        try:
            # Базовые проверки окружения для понятных сообщений об ошибках
            if not GOOGLE_SHEETS_CREDENTIALS_FILE:
                logger.error("GOOGLE_SHEETS_CREDENTIALS_FILE is not set (empty)")
                raise ValueError("GOOGLE_SHEETS_CREDENTIALS_FILE is empty")
            if not os.path.isfile(GOOGLE_SHEETS_CREDENTIALS_FILE):
                logger.error(f"Credentials file not found: {GOOGLE_SHEETS_CREDENTIALS_FILE}")
                raise FileNotFoundError(f"credentials.json not found at {GOOGLE_SHEETS_CREDENTIALS_FILE}")
            if not GOOGLE_SHEETS_URL:
                logger.error("GOOGLE_SHEETS_URL is not set (empty)")
                raise ValueError("GOOGLE_SHEETS_URL is empty")

            # Подсказка: логируем email сервисного аккаунта для раздачи доступа в таблице
            try:
                creds_preview = Credentials.from_service_account_file(GOOGLE_SHEETS_CREDENTIALS_FILE)
                if hasattr(creds_preview, 'service_account_email'):
                    logger.info(f"Using Google service account: {creds_preview.service_account_email}")
            except Exception:
                # не критично для продолжения, подробности ниже в exception()
                pass

            def get_creds():
                creds = Credentials.from_service_account_file(GOOGLE_SHEETS_CREDENTIALS_FILE)
                scoped = creds.with_scopes([
                    "https://spreadsheets.google.com/feeds",
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"
                ])
                return scoped
            
            self.agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)
            agc = await self.agcm.authorize()
            self.spreadsheet = await agc.open_by_url(GOOGLE_SHEETS_URL)
            
            logger.info("Google Sheets connection initialized successfully")
            
        except Exception as e:
            # Полная трассировка для быстрой диагностики
            logger.exception("Error initializing Google Sheets")
            raise
    
    @async_retry()
    async def get_project_names(self) -> List[str]:
        """Получение названий проектов (листов) с кэшированием"""
        cache_key = "project_names"
        cached = cache.get(cache_key)
        
        if cached:
            return cached
        
        try:
            worksheets = await self.spreadsheet.worksheets()
            project_names = [ws.title for ws in worksheets]
            
            cache.set(cache_key, project_names)
            logger.info(f"Found {len(project_names)} projects: {project_names}")
            return project_names
        except Exception as e:
            logger.error(f"Error getting project names: {e}")
            return []
    
    @async_retry()
    async def get_tasks_from_project(self, project_name: str) -> List[str]:
        """Получение задач из столбца D указанного проекта с кэшированием"""
        cache_key = f"tasks_{project_name}"
        cached = cache.get(cache_key)
        
        if cached:
            return cached
        
        try:
            worksheet = await self.spreadsheet.worksheet(project_name)
            tasks = await worksheet.col_values(4)  # Столбец D = 4
            
            if tasks:
                tasks = [task.strip() for task in tasks[1:] if task.strip()]
            
            cache.set(cache_key, tasks)
            logger.info(f"Found {len(tasks)} tasks in project {project_name}")
            return tasks
        except Exception as e:
            logger.error(f"Error getting tasks from project {project_name}: {e}")
            return []
    
    @async_retry()
    async def assign_task_to_user(self, project_name: str, task_index: int, user_name: str, user_phone: str) -> bool:
        """Запись данных исполнителя в столбцы E и F"""
        try:
            worksheet = await self.spreadsheet.worksheet(project_name)
            # Определяем реальную строку по тексту задачи (столбец D),
            # чтобы избежать смещений из-за пустых строк/фильтров
            task_name = await self.get_task_by_index(project_name, task_index)
            if not task_name:
                logger.error("assign_task_to_user: task_name not found by index")
                return False
            col_d = await worksheet.col_values(4)
            row_index = None
            for i, val in enumerate(col_d, start=1):
                if val.strip() == task_name.strip():
                    row_index = i
                    break
            if not row_index:
                logger.error(f"assign_task_to_user: row not found for task '{task_name}'")
                return False
            
            # Записываем имя и телефон одновременно
            await worksheet.batch_update([
                {
                    'range': f'E{row_index}',
                    'values': [[user_name]]
                },
                {
                    'range': f'F{row_index}',
                    'values': [[user_phone]]
                }
            ])
            
            # Инвалидируем кэш для этого проекта
            cache.delete(f"tasks_{project_name}")
            
            logger.info(f"Task assigned to {user_name} in project {project_name}, row {row_index}")
            return True
            
        except Exception as e:
            logger.error(f"Error assigning task to user: {e}")
            return False

    @async_retry()
    async def write_note_to_column_k(self, project_name: str, task_index: int, note_text: str) -> bool:
        """Записывает текст в столбец K (11) строки задачи, найденной по значению в D."""
        try:
            worksheet = await self.spreadsheet.worksheet(project_name)
            task_name = await self.get_task_by_index(project_name, task_index)
            if not task_name:
                logger.error("write_note_to_column_k: task_name not found by index")
                return False
            col_d = await worksheet.col_values(4)
            row_index = None
            for i, val in enumerate(col_d, start=1):
                if val.strip() == task_name.strip():
                    row_index = i
                    break
            if not row_index:
                logger.error(f"write_note_to_column_k: row not found for task '{task_name}'")
                return False

            await worksheet.update_acell(f'K{row_index}', note_text)
            logger.info(f"Note written to column K for project {project_name}, row {row_index}")
            return True
        except Exception as e:
            logger.error(f"Error writing note to column K: {e}")
            return False
    
    @async_retry()
    async def get_task_by_index(self, project_name: str, task_index: int) -> Optional[str]:
        """Получение конкретной задачи по индексу"""
        try:
            tasks = await self.get_tasks_from_project(project_name)
            if 0 <= task_index < len(tasks):
                return tasks[task_index]
            return None
        except Exception as e:
            logger.error(f"Error getting task by index: {e}")
            return None
    
    @async_retry()
    async def get_task_details(self, project_name: str, task_index: int) -> Optional[dict]:
        """Получение полной информации о задаче"""
        try:
            worksheet = await self.spreadsheet.worksheet(project_name)
            row_index = task_index + 2
            
            # Получаем всю строку
            row_data = await worksheet.row_values(row_index)
            
            if len(row_data) >= 6:
                return {
                    'task_name': row_data[3] if len(row_data) > 3 else '',
                    'assignee_name': row_data[4] if len(row_data) > 4 else '',
                    'assignee_phone': row_data[5] if len(row_data) > 5 else '',
                }
            return None
        except Exception as e:
            logger.error(f"Error getting task details: {e}")
            return None
    
    @async_retry()
    async def clear_task_assignment(self, project_name: str, task_index: int) -> bool:
        """Очистка назначения задачи"""
        try:
            worksheet = await self.spreadsheet.worksheet(project_name)
            row_index = task_index + 2
            
            await worksheet.batch_update([
                {
                    'range': f'E{row_index}',
                    'values': [['']]
                },
                {
                    'range': f'F{row_index}',
                    'values': [['']]
                }
            ])
            
            cache.delete(f"tasks_{project_name}")
            logger.info(f"Task assignment cleared in project {project_name}, row {row_index}")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing task assignment: {e}")
            return False
    
    async def refresh_cache(self):
        """Принудительное обновление кэша"""
        cache.clear()
        logger.info("Cache refreshed")

# Глобальный экземпляр менеджера Google Sheets
sheets_manager = GoogleSheetsManager()