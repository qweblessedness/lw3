#!/bin/bash
echo "🔄 Активація середовища..."
source venv/bin/activate

echo "🚀 Запуск Telegram-бота..."
python3 bot.py
