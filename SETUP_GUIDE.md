# 📖 Подробная инструкция по настройке

## ✅ Что уже настроено

Все необходимые данные уже добавлены в проект:

### 1. ✅ credentials.json
**Что это:** Ключи доступа к Google Sheets API от вашего Service Account

**Что внутри:**
- `client_email`: sxf-samarqand@data-centaur-466605-k7.iam.gserviceaccount.com
- `private_key`: Приватный ключ для аутентификации
- `project_id`: data-centaur-466605-k7

**Важно:** Этот email должен иметь доступ к вашей Google таблице!

### 2. ✅ .env файл
**Что это:** Конфигурация бота со всеми настройками

**Что внутри:**

```env
# Токен бота от @BotFather
BOT_TOKEN=7997794894:AAFu6bJXanh9BQWStTt9ZuqxgCYlCY_oDlE

# Настройки PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=111
POSTGRES_DB=kapital_bot

# Google Sheets
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json
GOOGLE_SHEETS_URL=https://docs.google.com/spreadsheets/d/1tISd6QbVU9bCx8pBed1w4izxDrnPhKc6WztTIJ7Kxf8/edit?gid=365492417#gid=365492417

# ID администраторов
ADMIN_IDS=5657091547,5048593195
```

## 🔧 Что нужно сделать перед запуском

### Шаг 1: Дать доступ к Google таблице

**ВАЖНО!** Откройте вашу Google таблицу и дайте доступ для:
```
sxf-samarqand@data-centaur-466605-k7.iam.gserviceaccount.com
```

**Как это сделать:**
1. Откройте таблицу: https://docs.google.com/spreadsheets/d/1tISd6QbVU9bCx8pBed1w4izxDrnPhKc6WztTIJ7Kxf8/
2. Нажмите кнопку "Настройки доступа" (Share)
3. Добавьте email: `sxf-samarqand@data-centaur-466605-k7.iam.gserviceaccount.com`
4. Выберите роль: "Редактор" (Editor)
5. Нажмите "Отправить"

### Шаг 2: Установить PostgreSQL

**Windows:**
1. Скачайте с https://www.postgresql.org/download/windows/
2. Установите с паролем `111` для пользователя `postgres`
3. Создайте базу данных `kapital_bot`

**Linux:**
```bash
sudo apt install postgresql postgresql-contrib
sudo -u postgres psql
CREATE DATABASE kapital_bot;
\q
```

### Шаг 3: Установить зависимости

**Windows:**
```cmd
install.bat
```

**Linux:**
```bash
chmod +x install.sh
./install.sh
```

## 🚀 Запуск бота

### Windows:
```cmd
run.bat
```

### Linux:
```bash
chmod +x run.sh
./run.sh
```

## 📊 Структура Google таблицы

Ваша таблица должна иметь такую структуру:

### Каждый лист = отдельный проект

| A | B | C | D (Задачи) | E (Исполнитель) | F (Телефон) |
|---|---|---|------------|-----------------|-------------|
| ... | ... | ... | Задача 1 | (заполнит бот) | (заполнит бот) |
| ... | ... | ... | Задача 2 | (заполнит бот) | (заполнит бот) |
| ... | ... | ... | Задача 3 | (заполнит бот) | (заполнит бот) |

**Важно:**
- Столбец D - названия задач (бот читает отсюда)
- Столбец E - имя исполнителя (бот записывает сюда)
- Столбец F - телефон исполнителя (бот записывает сюда)
- Первая строка - заголовки (бот пропускает)

## 🔍 Проверка работы

### 1. Проверка здоровья системы
```bash
python utils/health_check.py
```

Должно показать:
```
✅ Database OK - X users
✅ Google Sheets OK - X projects
✅ All systems operational
```

### 2. Проверка бота в Telegram

1. Найдите вашего бота в Telegram
2. Отправьте `/start`
3. Зарегистрируйтесь (отправьте контакт)
4. Нажмите "📋 Выбрать проект"
5. Должны появиться названия листов из таблицы

## 👥 Администраторы

В .env указаны два администратора:
- `5657091547`
- `5048593195`

**Что могут админы:**
- ✅ Одобрять/отклонять задачи
- 📊 Смотреть статистику
- 📑 Видеть все задачи
- 🔔 Получать уведомления о новых запросах

**Как узнать свой ID:**
1. Напишите боту @userinfobot в Telegram
2. Он покажет ваш ID
3. Добавьте его в ADMIN_IDS через запятую

## 🔐 Безопасность

### ⚠️ ВАЖНО!

**НЕ публикуйте эти файлы:**
- `.env` - содержит токен бота
- `credentials.json` - содержит приватный ключ

Они уже добавлены в `.gitignore`

**Если токен утек:**
1. Зайдите к @BotFather
2. Используйте команду `/revoke`
3. Получите новый токен
4. Обновите BOT_TOKEN в .env

## 🐛 Решение проблем

### Ошибка: "Database connection failed"
```bash
# Проверьте, запущен ли PostgreSQL
# Windows:
services.msc  # Найдите PostgreSQL

# Linux:
sudo systemctl status postgresql
sudo systemctl start postgresql
```

### Ошибка: "Google Sheets API error"
```bash
# Проверьте:
1. credentials.json существует
2. Email из credentials.json имеет доступ к таблице
3. URL таблицы правильный
```

### Ошибка: "Bot token is invalid"
```bash
# Проверьте BOT_TOKEN в .env
# Получите новый токен у @BotFather если нужно
```

## 📝 Логи

Все логи сохраняются в `bot.log`

**Просмотр логов:**
```bash
# Windows:
type bot.log

# Linux:
tail -f bot.log
```

## 🎯 Готово!

Если все настроено правильно:
1. ✅ PostgreSQL запущен
2. ✅ credentials.json на месте
3. ✅ Service Account имеет доступ к таблице
4. ✅ .env заполнен

Запускайте бота и он будет работать! 🚀

## 📞 Поддержка

При проблемах проверьте:
1. Логи в `bot.log`
2. Запустите `python utils/health_check.py`
3. Убедитесь что все сервисы запущены