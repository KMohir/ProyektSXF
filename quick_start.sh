#!/bin/bash

echo "🚀 Быстрый запуск бота..."

# Проверяем Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не установлен!"
    exit 1
fi

# Создаем venv если нет
if [ ! -d "venv" ]; then
    echo "📦 Создаем виртуальное окружение..."
    python3 -m venv venv
fi

# Активируем
echo "✅ Активируем виртуальное окружение..."
source venv/bin/activate

# Устанавливаем зависимости
echo "📦 Устанавливаем зависимости..."
pip install -q --upgrade pip
pip install -q aiogram==2.25.1
pip install -q asyncpg==0.29.0
pip install -q gspread-asyncio==2.0.0
pip install -q python-dotenv==1.0.0
pip install -q google-auth==2.23.4
pip install -q google-auth-oauthlib==1.1.0
pip install -q google-auth-httplib2==0.1.1
pip install -q tenacity==8.2.3

echo "✅ Зависимости установлены!"
echo ""
echo "🚀 Запускаем бота..."
echo ""

# Запускаем
python3 run.py
