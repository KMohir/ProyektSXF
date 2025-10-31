@echo off
REM Скрипт установки зависимостей для Windows

echo Installing dependencies...

REM Проверка Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python 3.8 or higher.
    exit /b 1
)

REM Создание виртуального окружения
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Активация виртуального окружения
call venv\Scripts\activate.bat

REM Обновление pip
python -m pip install --upgrade pip

REM Установка зависимостей
pip install -r requirements.txt

echo Installation complete!
echo To activate virtual environment, run: venv\Scripts\activate.bat
echo To start the bot, run: run.bat

pause