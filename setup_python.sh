#!/bin/bash

echo "🔧 Настройка правильной версии Python..."

# Проверяем текущую версию
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Текущая версия Python: $PYTHON_VERSION"

# Проверяем доступные версии Python
if command -v python3.12 &> /dev/null; then
    echo "✅ Найден Python 3.12"
    PYTHON_CMD="python3.12"
elif command -v python3.11 &> /dev/null; then
    echo "✅ Найден Python 3.11"
    PYTHON_CMD="python3.11"
elif command -v python3.10 &> /dev/null; then
    echo "✅ Найден Python 3.10"
    PYTHON_CMD="python3.10"
else
    echo "❌ Нужен Python 3.10, 3.11 или 3.12"
    echo "Установите: sudo apt install python3.11 python3.11-venv"
    exit 1
fi

echo "Используем: $PYTHON_CMD"

# Удаляем старое виртуальное окружение
if [ -d "venv" ]; then
    echo "🗑️  Удаляем старое виртуальное окружение..."
    rm -rf venv
fi

# Создаем новое с правильной версией Python
echo "📦 Создаем виртуальное окружение с $PYTHON_CMD..."
$PYTHON_CMD -m venv venv

# Активируем
source venv/bin/activate

# Обновляем pip
echo "📦 Обновляем pip..."
pip install --upgrade pip setuptools wheel

# Устанавливаем зависимости
echo "📦 Устанавливаем зависимости..."
pip install aiogram==2.25.1
pip install asyncpg==0.29.0
pip install gspread-asyncio==2.0.0
pip install python-dotenv==1.0.0
pip install google-auth==2.23.4
pip install google-auth-oauthlib==1.1.0
pip install google-auth-httplib2==0.1.1
pip install tenacity==8.2.3

echo ""
echo "✅ Установка завершена!"
echo ""
echo "🚀 Запускаем бота..."
python3 run.py
