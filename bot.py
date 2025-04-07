"""Telegram-бот для підтримки прифронтових територій."""

import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
users = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробка команди /start — вітання та інструкція."""
    user = update.message.from_user
    users[user.id] = user.username
    await update.message.reply_text(
        "Вітаємо! Я бот підтримки для осіб, що перебувають у прифронтовій зоні. Ось деякі команди:\n"
        "/situation - Поточна ситуація\n"
        "/resources - Доступні ресурси та послуги\n"
        "/communicate - Спілкування\n"
        "/safety - Інформація про безпеку\n"
        "/other - Інші ресурси"
    )


async def communicate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробка команди /communicate — кнопки для вибору типу спілкування."""
    keyboard = [
        [InlineKeyboardButton("Спілкуйтеся з іншими людьми в прифронтовій зоні", callback_data="show_users")],
        [InlineKeyboardButton("Спілкуйтеся з тими, хто підтримує", callback_data="support")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Спілкування:", reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробка натискань на інлайн-кнопки."""
    query = update.callback_query
    await query.answer()

    if query.data == "show_users":
        if users:
            keyboard = [
                [InlineKeyboardButton(username, callback_data=f"chat_{user_id}")]
                for user_id, username in users.items()
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Оберіть користувача:", reply_markup=reply_markup)
        else:
            await query.edit_message_text("Наразі немає доступних користувачів для спілкування.")
    elif query.data == "support":
        await query.edit_message_text("Підтримка наразі недоступна. Спробуйте пізніше.")


async def chat_with_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Вибір користувача для спілкування."""
    query = update.callback_query
    await query.answer()

    user_id = int(query.data.split("_")[1])
    if user_id in users:
        await query.edit_message_text(
            f"Ви обрали {users[user_id]}. Напишіть /send {user_id} <повідомлення> для зв'язку."
        )
    else:
        await query.edit_message_text("Цей користувач наразі недоступний.")


async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Надсилання повідомлення обраному користувачу."""
    try:
        user_id = int(context.args[0])
        message_text = " ".join(context.args[1:])
        if user_id in users:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"Повідомлення від {update.message.from_user.username}: {message_text}",
            )
            await update.message.reply_text(f"Повідомлення надіслано користувачу {users[user_id]}.")
        else:
            await update.message.reply_text("Користувач не знайдений.")
    except (IndexError, ValueError):
        await update.message.reply_text("Формат: /send <user_id> <повідомлення>.")


async def situation(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Інформація про поточну ситуацію."""
    await update.message.reply_text(
        "Поточна ситуація в прифронтовій зоні:\n"
        "1. Розташування бомбосховищ: ...\n"
        "2. Маршрути евакуації: ...\n"
        "3. Інші важливі дані: ..."
    )


async def resources(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Інформація про доступні ресурси."""
    await update.message.reply_text(
        "Доступні ресурси:\n"
        "1. Медична допомога: ...\n"
        "2. Психологічна підтримка: ...\n"
        "3. Правова допомога: ..."
    )


async def safety(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Поради з безпеки."""
    await update.message.reply_text(
        "Інформація про безпеку:\n"
        "1. Як залишатися в безпеці: ...\n"
        "2. Як уникати обстрілів: ...\n"
        "3. Як знайти бомбосховище: ..."
    )


async def other(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Інші корисні ресурси."""
    await update.message.reply_text(
        "Інші ресурси:\n"
        "1. Карти: ...\n"
        "2. Новини: ...\n"
        "3. Погода: ..."
    )


def main() -> None:
    """Запуск бота."""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("situation", situation))
    application.add_handler(CommandHandler("resources", resources))
    application.add_handler(CommandHandler("communicate", communicate))
    application.add_handler(CommandHandler("safety", safety))
    application.add_handler(CommandHandler("other", other))
    application.add_handler(CommandHandler("send", send_message))

    application.add_handler(CallbackQueryHandler(button_handler, pattern="^show_users$"))
    application.add_handler(CallbackQueryHandler(chat_with_user, pattern="^chat_"))

    application.run_polling()


if __name__ == "__main__":
    main()
