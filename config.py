import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in .env file")

# PostgreSQL Configuration
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', 5432))
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')

if not all([POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB]):
    raise ValueError("PostgreSQL configuration is incomplete in .env file")

# Google Sheets Configuration
GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE')
GOOGLE_SHEETS_URL = os.getenv('GOOGLE_SHEETS_URL')

if not GOOGLE_SHEETS_CREDENTIALS_FILE or not GOOGLE_SHEETS_URL:
    raise ValueError("Google Sheets configuration is incomplete in .env file")

# Admin Configuration
ADMIN_IDS = [int(admin_id.strip()) for admin_id in os.getenv('ADMIN_IDS', '').split(',') if admin_id.strip()]

if not ADMIN_IDS:
    raise ValueError("ADMIN_IDS is not set in .env file")

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'bot.log')

# Bot Configuration
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
RETRY_DELAY = int(os.getenv('RETRY_DELAY', 5))
CACHE_TTL = int(os.getenv('CACHE_TTL', 300))

# Database URL
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Messages
MESSAGES = {
    'welcome_new': "Добро пожаловать в Task Manager Bot! 🤖\n\n"
                   "Для начала работы необходимо зарегистрироваться.\n"
                   "Пожалуйста, отправьте свой контакт, нажав на кнопку ниже:",
    'welcome_back': "Добро пожаловать обратно, {name}! 👋\nВыберите действие:",
    'registration_success': "✅ Регистрация успешно завершена!\n\n"
                           "Имя: {name}\n"
                           "Телефон: {phone}\n\n"
                           "Теперь вы можете выбирать проекты и задачи:",
    'registration_error': "❌ Произошла ошибка при регистрации. Попробуйте еще раз.",
    'not_registered': "❌ Вы не зарегистрированы. Используйте команду /start для регистрации.",
    'no_projects': "❌ Проекты не найдены. Попробуйте позже.",
    'no_tasks': "❌ В проекте '{project}' нет доступных задач.",
    'request_sent': "✅ Ваш запрос отправлен на рассмотрение!\n\n"
                   "📋 Проект: {project}\n"
                   "📝 Задача: {task}\n\n"
                   "Ожидайте ответа от администратора.",
    'request_approved': "🎉 Ваш запрос одобрен!\n\n"
                       "📋 Проект: {project}\n"
                       "📝 Задача: {task}\n\n"
                       "Можете приступать к выполнению!",
    'request_rejected': "😔 Ваш запрос отклонен\n\n"
                       "📋 Проект: {project}\n"
                       "📝 Задача: {task}\n\n"
                       "Вы можете выбрать другую задачу.",
    'admin_new_request': "🔔 Новый запрос на задачу!\n\n"
                        "👤 Пользователь: {name}\n"
                        "📞 Телефон: {phone}\n"
                        "🆔 User ID: {user_id}\n"
                        "📋 Проект: {project}\n"
                        "📝 Задача: {task}",
    'admin_approved': "✅ Задача одобрена и назначена!\n\n"
                     "👤 Пользователь: {name}\n"
                     "📞 Телефон: {phone}\n"
                     "📋 Проект: {project}\n"
                     "📝 Задача: {task}",
    'admin_rejected': "❌ Задача отклонена\n\n"
                     "👤 Пользователь: {name}\n"
                     "📞 Телефон: {phone}\n"
                     "📋 Проект: {project}\n"
                     "📝 Задача: {task}",
}