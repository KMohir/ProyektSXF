#!/bin/bash

# Скрипт для настройки systemd сервиса

if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Получаем текущую директорию
CURRENT_DIR=$(pwd)
CURRENT_USER=$(logname)

echo "Setting up systemd service..."
echo "Current directory: $CURRENT_DIR"
echo "Current user: $CURRENT_USER"

# Создаем директорию для логов
mkdir -p /var/log/telegram-bot
chown $CURRENT_USER:$CURRENT_USER /var/log/telegram-bot

# Копируем и настраиваем service файл
cp telegram-bot.service /etc/systemd/system/
sed -i "s|/path/to/telegram-task-bot|$CURRENT_DIR|g" /etc/systemd/system/telegram-bot.service
sed -i "s|your_user|$CURRENT_USER|g" /etc/systemd/system/telegram-bot.service
sed -i "s|your_group|$CURRENT_USER|g" /etc/systemd/system/telegram-bot.service

# Перезагружаем systemd
systemctl daemon-reload

echo "✅ Systemd service installed!"
echo ""
echo "To enable and start the service:"
echo "  sudo systemctl enable telegram-bot"
echo "  sudo systemctl start telegram-bot"
echo ""
echo "To check status:"
echo "  sudo systemctl status telegram-bot"
echo ""
echo "To view logs:"
echo "  sudo journalctl -u telegram-bot -f"