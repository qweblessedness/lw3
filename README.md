## 🚀 Інструкція для розробника

Ця інструкція допоможе налаштувати проєкт з нуля на чистій системі.

---

### 🔧 Необхідне програмне забезпечення

- Python 3.10 або вище: https://www.python.org/downloads/
- Git: https://git-scm.com/

---

### 🛠 Кроки встановлення

1. **Клонувати репозиторій**
git clone https://github.com/qweblessedness/lw3.git
cd bakalavr
Створити та активувати віртуальне середовище

python -m venv venv
venv\Scripts\activate
   
Встановити залежності
pip install -r requirements.txt
Налаштувати змінні середовища
Створи файл .env у корені проєкту з таким вмістом:
BOT_TOKEN=your_telegram_bot_token_here
Запуск проєкту в режимі розробки
python bot.py
📦 Базові команди бота
/start – Привітання та інструкції
/situation, /resources, /safety, /other – Інформаційні блоки
/communicate – Інлайн-кнопки для спілкування
/send <id> <текст> – Пряме повідомлення користувачу
