#!/bin/bash

# Скрипт для запуска бота с автоматическим перезапуском

while true; do
    echo "Starting bot..."
    python3 run.py
    
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo "Bot stopped normally"
        break
    else
        echo "Bot crashed with exit code $EXIT_CODE. Restarting in 5 seconds..."
        sleep 5
    fi
done