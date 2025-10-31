import asyncpg
from typing import Optional, List, Dict
from utils.logger import logger
from utils.decorators import async_retry
from config import DATABASE_URL

class Database:
    def __init__(self):
        self.pool = None
    
    @async_retry(max_attempts=5)
    async def create_pool(self):
        """Создание пула соединений с базой данных"""
        try:
            self.pool = await asyncpg.create_pool(
                DATABASE_URL,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            await self.create_tables()
            logger.info("Database pool created successfully")
        except Exception as e:
            logger.error(f"Error creating database pool: {e}")
            raise
    
    async def create_tables(self):
        """Создание необходимых таблиц"""
        async with self.pool.acquire() as conn:
            # Таблица пользователей
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    phone VARCHAR(20) NOT NULL,
                    is_admin BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE,
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица задач
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT REFERENCES users(user_id),
                    project_name VARCHAR(255) NOT NULL,
                    task_name TEXT NOT NULL,
                    task_index INTEGER NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    admin_id BIGINT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            ''')
            
            # Таблица логов действий
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS action_logs (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    action VARCHAR(100) NOT NULL,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Индексы для оптимизации
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_name)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_logs_user_id ON action_logs(user_id)')
            
            logger.info("Tables and indexes created successfully")
    
    @async_retry()
    async def register_user(self, user_id: int, name: str, phone: str) -> bool:
        """Регистрация нового пользователя"""
        async with self.pool.acquire() as conn:
            try:
                await conn.execute('''
                    INSERT INTO users (user_id, name, phone) 
                    VALUES ($1, $2, $3) 
                    ON CONFLICT (user_id) DO UPDATE 
                    SET name = $2, phone = $3, last_activity = CURRENT_TIMESTAMP
                ''', user_id, name, phone)
                
                await self.log_action(user_id, 'register', f'User registered: {name}')
                logger.info(f"User {user_id} registered successfully")
                return True
            except Exception as e:
                logger.error(f"Error registering user {user_id}: {e}")
                return False
    
    @async_retry()
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Получение информации о пользователе"""
        async with self.pool.acquire() as conn:
            try:
                row = await conn.fetchrow('SELECT * FROM users WHERE user_id = $1', user_id)
                if row:
                    # Обновляем время последней активности
                    await conn.execute(
                        'UPDATE users SET last_activity = CURRENT_TIMESTAMP WHERE user_id = $1',
                        user_id
                    )
                return dict(row) if row else None
            except Exception as e:
                logger.error(f"Error getting user {user_id}: {e}")
                return None
    
    @async_retry()
    async def create_task_request(self, user_id: int, project_name: str, task_name: str, task_index: int) -> Optional[int]:
        """Создание запроса на задачу"""
        async with self.pool.acquire() as conn:
            try:
                task_id = await conn.fetchval('''
                    INSERT INTO tasks (user_id, project_name, task_name, task_index) 
                    VALUES ($1, $2, $3, $4) 
                    RETURNING id
                ''', user_id, project_name, task_name, task_index)
                
                await self.log_action(user_id, 'task_request', f'Project: {project_name}, Task: {task_name}')
                logger.info(f"Task request created with ID {task_id}")
                return task_id
            except Exception as e:
                logger.error(f"Error creating task request: {e}")
                return None
    
    @async_retry()
    async def update_task_status(self, user_id: int, project_name: str, task_index: int, status: str, admin_id: Optional[int] = None) -> bool:
        """Обновление статуса задачи"""
        async with self.pool.acquire() as conn:
            try:
                query = '''
                    UPDATE tasks 
                    SET status = $1, updated_at = CURRENT_TIMESTAMP, admin_id = $5
                '''
                
                if status == 'completed':
                    query += ', completed_at = CURRENT_TIMESTAMP'
                
                query += ' WHERE user_id = $2 AND project_name = $3 AND task_index = $4'
                
                await conn.execute(query, status, user_id, project_name, task_index, admin_id)
                
                await self.log_action(user_id, 'task_status_update', f'Status: {status}, Project: {project_name}')
                logger.info(f"Task status updated to {status} for user {user_id}")
                return True
            except Exception as e:
                logger.error(f"Error updating task status: {e}")
                return False
    
    @async_retry()
    async def get_user_tasks(self, user_id: int, status: Optional[str] = None) -> List[Dict]:
        """Получение задач пользователя"""
        async with self.pool.acquire() as conn:
            try:
                if status:
                    rows = await conn.fetch('''
                        SELECT * FROM tasks 
                        WHERE user_id = $1 AND status = $2 
                        ORDER BY created_at DESC
                    ''', user_id, status)
                else:
                    rows = await conn.fetch('''
                        SELECT * FROM tasks 
                        WHERE user_id = $1 
                        ORDER BY created_at DESC
                    ''', user_id)
                
                return [dict(row) for row in rows]
            except Exception as e:
                logger.error(f"Error getting user tasks: {e}")
                return []
    
    @async_retry()
    async def get_all_tasks(self, status: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Получение всех задач (для администраторов)"""
        async with self.pool.acquire() as conn:
            try:
                if status:
                    rows = await conn.fetch('''
                        SELECT t.*, u.name, u.phone 
                        FROM tasks t
                        JOIN users u ON t.user_id = u.user_id
                        WHERE t.status = $1
                        ORDER BY t.created_at DESC
                        LIMIT $2
                    ''', status, limit)
                else:
                    rows = await conn.fetch('''
                        SELECT t.*, u.name, u.phone 
                        FROM tasks t
                        JOIN users u ON t.user_id = u.user_id
                        ORDER BY t.created_at DESC
                        LIMIT $1
                    ''', limit)
                
                return [dict(row) for row in rows]
            except Exception as e:
                logger.error(f"Error getting all tasks: {e}")
                return []
    
    @async_retry()
    async def get_statistics(self) -> Dict:
        """Получение статистики"""
        async with self.pool.acquire() as conn:
            try:
                stats = {}
                
                # Общее количество пользователей
                stats['total_users'] = await conn.fetchval('SELECT COUNT(*) FROM users')
                
                # Активные пользователи (за последние 7 дней)
                stats['active_users'] = await conn.fetchval('''
                    SELECT COUNT(*) FROM users 
                    WHERE last_activity > CURRENT_TIMESTAMP - INTERVAL '7 days'
                ''')
                
                # Статистика по задачам
                stats['total_tasks'] = await conn.fetchval('SELECT COUNT(*) FROM tasks')
                stats['pending_tasks'] = await conn.fetchval("SELECT COUNT(*) FROM tasks WHERE status = 'pending'")
                stats['approved_tasks'] = await conn.fetchval("SELECT COUNT(*) FROM tasks WHERE status = 'approved'")
                stats['rejected_tasks'] = await conn.fetchval("SELECT COUNT(*) FROM tasks WHERE status = 'rejected'")
                stats['completed_tasks'] = await conn.fetchval("SELECT COUNT(*) FROM tasks WHERE status = 'completed'")
                
                # Топ проектов
                top_projects = await conn.fetch('''
                    SELECT project_name, COUNT(*) as count 
                    FROM tasks 
                    GROUP BY project_name 
                    ORDER BY count DESC 
                    LIMIT 5
                ''')
                stats['top_projects'] = [dict(row) for row in top_projects]
                
                return stats
            except Exception as e:
                logger.error(f"Error getting statistics: {e}")
                return {}
    
    @async_retry()
    async def log_action(self, user_id: int, action: str, details: str = None):
        """Логирование действий пользователя"""
        async with self.pool.acquire() as conn:
            try:
                await conn.execute('''
                    INSERT INTO action_logs (user_id, action, details) 
                    VALUES ($1, $2, $3)
                ''', user_id, action, details)
            except Exception as e:
                logger.error(f"Error logging action: {e}")
    
    async def close(self):
        """Закрытие пула соединений"""
        if self.pool:
            await self.pool.close()
            logger.info("Database pool closed")

# Глобальный экземпляр базы данных
db = Database()