# 🤖 Telegram Task Manager Bot

Масштабируемый Telegram-бот для назначения задач сотрудникам с интеграцией Google Sheets и PostgreSQL.

## ✨ Основные возможности

### Для пользователей:
- ✅ **Регистрация** через отправку контакта
- 📋 **Выбор проектов** из Google Sheets
- 📝 **Выбор задач** с автоматической отправкой запроса
- 🔔 **Уведомления** о статусе запроса
- 📊 **Просмотр своих задач**

### Для администраторов:
- 🔔 **Уведомления** о новых запросах
- ✅/❌ **Одобрение/Отклонение** задач
- 📊 **Статистика** по боту и пользователям
- 📑 **Просмотр всех задач**
- 🔄 **Автоматическая запись** в Google Sheets

## 🏗️ Архитектура

```
telegram-task-bot/
├── bot.py                  # Основная логика бота
├── run.py                  # Скрипт запуска с обработкой ошибок
├── config.py               # Конфигурация и настройки
├── db.py                   # Работа с PostgreSQL
├── sheets.py               # Интеграция с Google Sheets
├── keyboards.py            # Клавиатуры бота
├── utils/
│   ├── __init__.py
│   ├── logger.py          # Система логирования
│   ├── cache.py           # Кэширование данных
│   └── decorators.py      # Декораторы для повторных попыток
├── requirements.txt        # Зависимости
├── .env                   # Переменные окружения
├── credentials.json       # Ключи Google Sheets API
├── install.sh/bat         # Скрипты установки
└── run.sh/bat             # Скрипты запуска
```

## 🚀 Быстрый старт

### Linux/Mac:

```bash
# 1. Установка зависимостей
chmod +x install.sh
./install.sh

# 2. Настройка .env файла
# Отредактируйте .env и добавьте свои данные

# 3. Добавьте credentials.json для Google Sheets

# 4. Запуск бота
chmod +x run.sh
./run.sh
```

### Windows:

```cmd
# 1. Установка зависимостей
install.bat

# 2. Настройка .env файла
# Отредактируйте .env и добавьте свои данные

# 3. Добавьте credentials.json для Google Sheets

# 4. Запуск бота
run.bat
```

## ⚙️ Настройка

### 1. Переменные окружения (.env)

```env
# Telegram Bot Token (получить у @BotFather)
BOT_TOKEN=your_bot_token

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=kapital_bot

# Google Sheets
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json
GOOGLE_SHEETS_URL=your_spreadsheet_url

# Admin IDs (через запятую)
ADMIN_IDS=123456789,987654321

# Опционально
LOG_LEVEL=INFO
LOG_FILE=bot.log
MAX_RETRIES=3
RETRY_DELAY=5
CACHE_TTL=300
```

### 2. Google Sheets API

1. Создайте проект в [Google Cloud Console](https://console.cloud.google.com/)
2. Включите Google Sheets API
3. Создайте Service Account
4. Скачайте JSON-файл с ключами → `credentials.json`
5. Предоставьте доступ к таблице для email из Service Account

### 3. PostgreSQL

```bash
# Создание базы данных
createdb kapital_bot

# Или через psql
psql -U postgres
CREATE DATABASE kapital_bot;
```

### 4. Структура Google Sheets

Каждый лист = отдельный проект

| A | B | C | D (Задачи) | E (Исполнитель) | F (Телефон) |
|---|---|---|------------|-----------------|-------------|
| ... | ... | ... | Задача 1 | | |
| ... | ... | ... | Задача 2 | | |

## 📊 База данных

### Таблицы:

- **users** - Пользователи
- **tasks** - Задачи и запросы
- **action_logs** - Логи действий

## 🔧 Технологии

- **aiogram 2.x** - Telegram Bot Framework
- **PostgreSQL** - База данных
- **asyncpg** - Асинхронный драйвер PostgreSQL
- **Google Sheets API** - Интеграция с таблицами
- **gspread-asyncio** - Асинхронная работа с Google Sheets
- **tenacity** - Повторные попытки при ошибках

## 📝 Команды бота

- `/start` - Регистрация / Главное меню
- `/help` - Справка
- `/cancel` - Отменить текущее действие

## 🛡️ Надежность

- ✅ **Автоматический перезапуск** при ошибках
- ✅ **Повторные попытки** для сетевых операций
- ✅ **Кэширование** данных из Google Sheets
- ✅ **Логирование** всех действий
- ✅ **Обработка ошибок** на всех уровнях
- ✅ **Middleware** для мониторинга
- ✅ **Connection pooling** для БД

## 📈 Масштабируемость

- Асинхронная архитектура
- Пул соединений с БД (5-20 соединений)
- Кэширование с TTL
- Индексы в БД для быстрых запросов
- Batch операции с Google Sheets

## 🔍 Мониторинг

Логи сохраняются в `bot.log` с ротацией (макс. 10MB × 5 файлов)

```bash
# Просмотр логов в реальном времени
tail -f bot.log
```

## 🐛 Отладка

```bash
# Включить DEBUG логирование
# В .env:
LOG_LEVEL=DEBUG

# Проверка подключения к БД
python -c "import asyncio; from db import db; asyncio.run(db.create_pool())"

# Проверка Google Sheets
python -c "import asyncio; from sheets import sheets_manager; asyncio.run(sheets_manager.initialize())"
```

## 📦 Деплой

### Systemd (Linux):

```ini
[Unit]
Description=Telegram Task Manager Bot
After=network.target postgresql.service

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/bot
ExecStart=/path/to/bot/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

### Docker:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run.py"]
```

## 🤝 Поддержка

При возникновении проблем:
1. Проверьте логи в `bot.log`
2. Убедитесь, что все переменные в `.env` заполнены
3. Проверьте доступ к PostgreSQL и Google Sheets

## 📄 Лицензия

MIT License