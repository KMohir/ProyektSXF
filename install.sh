#!/bin/bash

# Скрипт установки зависимостей

echo "Installing dependencies..."

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Создание виртуального окружения
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Активация виртуального окружения
source venv/bin/activate

# Обновление pip
pip install --upgrade pip

# Установка зависимостей
pip install -r requirements.txt

echo "Installation complete!"
echo "To activate virtual environment, run: source venv/bin/activate"
echo "To start the bot, run: ./run.sh"