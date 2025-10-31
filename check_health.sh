#!/bin/bash

# Проверка здоровья системы

echo "Checking system health..."
python3 utils/health_check.py

if [ $? -eq 0 ]; then
    echo "All systems operational!"
else
    echo "Some systems are down!"
fi