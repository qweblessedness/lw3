@echo off
echo 🔄 Активація середовища...
call venv\Scripts\activate

echo 🚀 Запуск бота у режимі розробки...
python bot.py
pause
