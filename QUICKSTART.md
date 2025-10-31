# ⚡ Быстрый старт

## 🎯 За 5 минут до запуска

### Windows

```cmd
REM 1. Установка
install.bat

REM 2. Настройка
copy .env.example .env
notepad .env

REM 3. Добавьте credentials.json

REM 4. Запуск
run.bat
```

### Linux/Mac

```bash
# 1. Установка
chmod +x install.sh && ./install.sh

# 2. Настройка
cp .env.example .env && nano .env

# 3. Добавьте credentials.json

# 4. Запуск
chmod +x run.sh && ./run.sh
```

## 📋 Что нужно настроить в .env

```env
BOT_TOKEN=получить_у_@BotFather
POSTGRES_PASSWORD=ваш_пароль
GOOGLE_SHEETS_URL=ссылка_на_таблицу
ADMIN_IDS=ваш_telegram_id
```

## 🔑 Как получить credentials.json

1. Перейдите на https://console.cloud.google.com/
2. Создайте проект
3. Включите Google Sheets API
4. Создайте Service Account
5. Скачайте JSON → сохраните как `credentials.json`
6. Дайте доступ к таблице email из JSON

## ✅ Проверка работы

```bash
# Проверка здоровья системы
python utils/health_check.py

# Если все ОК - запускайте бота!
```

## 🆘 Проблемы?

- Проверьте `bot.log`
- Убедитесь что PostgreSQL запущен
- Проверьте доступ к Google Sheets
- Читайте полную документацию в README.md