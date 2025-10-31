# 🚀 Руководство по развертыванию

## Содержание
1. [Локальная разработка](#локальная-разработка)
2. [Развертывание на VPS](#развертывание-на-vps)
3. [Docker развертывание](#docker-развертывание)
4. [Мониторинг и обслуживание](#мониторинг-и-обслуживание)

---

## Локальная разработка

### Windows

```cmd
# 1. Установка зависимостей
install.bat

# 2. Настройка .env
copy .env.example .env
# Отредактируйте .env

# 3. Запуск PostgreSQL (если локально)
# Установите PostgreSQL с официального сайта

# 4. Запуск бота
run.bat
```

### Linux/Mac

```bash
# 1. Установка зависимостей
chmod +x install.sh
./install.sh

# 2. Настройка .env
cp .env.example .env
# Отредактируйте .env

# 3. Запуск PostgreSQL
sudo systemctl start postgresql

# 4. Запуск бота
chmod +x run.sh
./run.sh
```

---

## Развертывание на VPS

### Требования
- Ubuntu 20.04+ / Debian 11+
- Python 3.8+
- PostgreSQL 12+
- 1GB RAM минимум
- 10GB свободного места

### Шаг 1: Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка зависимостей
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib git

# Создание пользователя для бота
sudo useradd -m -s /bin/bash botuser
sudo su - botuser
```

### Шаг 2: Клонирование проекта

```bash
cd ~
git clone https://github.com/your-repo/telegram-task-bot.git
cd telegram-task-bot
```

### Шаг 3: Настройка PostgreSQL

```bash
# Переключаемся на пользователя postgres
sudo -u postgres psql

# В psql:
CREATE DATABASE kapital_bot;
CREATE USER botuser WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE kapital_bot TO botuser;
\q
```

### Шаг 4: Настройка бота

```bash
# Установка зависимостей
./install.sh

# Настройка .env
cp .env.example .env
nano .env  # Заполните все переменные

# Добавление credentials.json
nano credentials.json  # Вставьте JSON от Google Service Account
```

### Шаг 5: Настройка systemd

```bash
# Установка сервиса
sudo ./setup_systemd.sh

# Запуск бота
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot

# Проверка статуса
sudo systemctl status telegram-bot
```

### Шаг 6: Настройка логирования

```bash
# Просмотр логов
sudo journalctl -u telegram-bot -f

# Или файловые логи
tail -f bot.log
```

---

## Docker развертывание

### Требования
- Docker 20.10+
- Docker Compose 2.0+

### Быстрый старт

```bash
# 1. Клонирование
git clone https://github.com/your-repo/telegram-task-bot.git
cd telegram-task-bot

# 2. Настройка .env
cp .env.example .env
nano .env

# 3. Добавление credentials.json
nano credentials.json

# 4. Запуск
docker-compose up -d

# 5. Просмотр логов
docker-compose logs -f bot
```

### Управление

```bash
# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Обновление
git pull
docker-compose build
docker-compose up -d

# Резервное копирование БД
docker-compose exec postgres pg_dump -U postgres kapital_bot > backup.sql

# Восстановление БД
docker-compose exec -T postgres psql -U postgres kapital_bot < backup.sql
```

---

## Мониторинг и обслуживание

### Проверка здоровья

```bash
# Ручная проверка
python utils/health_check.py

# Или через скрипт
./check_health.sh  # Linux
check_health.bat   # Windows
```

### Автоматический мониторинг

```bash
# Настройка cron для мониторинга
crontab -e

# Добавьте строки из crontab.example
# Например:
0 */6 * * * cd /home/botuser/telegram-task-bot && /home/botuser/telegram-task-bot/venv/bin/python monitor.py
```

### Резервное копирование

```bash
# Ручное резервное копирование
python utils/backup.py

# Автоматическое (через cron)
0 3 * * * cd /home/botuser/telegram-task-bot && /home/botuser/telegram-task-bot/venv/bin/python utils/backup.py
```

### Обновление бота

```bash
# С systemd
sudo systemctl stop telegram-bot
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl start telegram-bot

# С Docker
docker-compose down
git pull
docker-compose build
docker-compose up -d
```

### Просмотр логов

```bash
# Systemd
sudo journalctl -u telegram-bot -f

# Docker
docker-compose logs -f bot

# Файловые логи
tail -f bot.log
tail -f logs/bot.log
```

### Очистка логов

```bash
# Ручная очистка
find . -name "*.log.*" -mtime +30 -delete

# Автоматическая (через cron)
0 0 * * 0 find /home/botuser/telegram-task-bot/logs -name "*.log.*" -mtime +30 -delete
```

---

## Безопасность

### Рекомендации

1. **Не коммитьте секреты**
   ```bash
   # Проверьте .gitignore
   cat .gitignore
   ```

2. **Используйте сильные пароли**
   - PostgreSQL
   - Telegram Bot Token

3. **Ограничьте доступ к файлам**
   ```bash
   chmod 600 .env
   chmod 600 credentials.json
   ```

4. **Настройте firewall**
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw enable
   ```

5. **Регулярные обновления**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

---

## Troubleshooting

### Бот не запускается

```bash
# Проверьте логи
sudo journalctl -u telegram-bot -n 50

# Проверьте конфигурацию
python -c "from config import *; print('Config OK')"

# Проверьте подключения
python utils/health_check.py
```

### Ошибки БД

```bash
# Проверьте PostgreSQL
sudo systemctl status postgresql

# Проверьте подключение
psql -U postgres -d kapital_bot -c "SELECT 1"

# Пересоздайте таблицы
python -c "import asyncio; from db import db; asyncio.run(db.create_pool())"
```

### Ошибки Google Sheets

```bash
# Проверьте credentials.json
cat credentials.json | python -m json.tool

# Проверьте доступ к таблице
# Email из credentials.json должен иметь доступ к таблице
```

---

## Производительность

### Оптимизация PostgreSQL

```sql
-- В postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB
```

### Мониторинг производительности

```bash
# CPU и память
htop

# Процессы Python
ps aux | grep python

# Размер БД
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('kapital_bot'));"

# Активные соединения
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity WHERE datname='kapital_bot';"
```

---

## Контакты и поддержка

При возникновении проблем:
1. Проверьте логи
2. Изучите документацию
3. Создайте issue на GitHub