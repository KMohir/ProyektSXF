@echo off
REM Скрипт для запуска бота на Windows с автоматическим перезапуском

:start
echo Starting bot...
python run.py

if %ERRORLEVEL% EQU 0 (
    echo Bot stopped normally
    goto end
) else (
    echo Bot crashed with exit code %ERRORLEVEL%. Restarting in 5 seconds...
    timeout /t 5 /nobreak
    goto start
)

:end
pause