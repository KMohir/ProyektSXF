@echo off
REM Проверка здоровья системы

echo Checking system health...
python utils/health_check.py

if %ERRORLEVEL% EQU 0 (
    echo All systems operational!
) else (
    echo Some systems are down!
)

pause