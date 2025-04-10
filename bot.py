"""Telegram-бот для підтримки прифронтових територій."""

import os
import uuid
import traceback
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from logging.handlers import RotatingFileHandler

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
log_level = os.getenv("LOG_LEVEL", "INFO").upper()

log_file = RotatingFileHandler("bot.log", maxBytes=1_000_000, backupCount=3)
log_file.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))

logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    handlers=[
        log_file,
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

users = {}



import sentry_sdk

sentry_sdk.init(
    dsn="https://2c650f462ee2a7a00076f2b5f935c076@o4509127048429568.ingest.de.sentry.io/4509127064682576",
    send_default_pii=True,
)

MESSAGES = {
    "start": "Вітаємо! Я бот підтримки для осіб, що перебувають у прифронтовій зоні. Ось деякі команди:\n/start - Початок\n/situation - Ситуація\n/resources - Ресурси\n/communicate - Спілкування\n/safety - Безпека\n/other - Інше",
    "choose_user": "Оберіть користувача:",
    "no_users": "Наразі немає користувачів для спілкування.",
    "support_unavailable": "Підтримка наразі недоступна. Спробуйте пізніше.",
    "message_sent": "Повідомлення надіслано користувачу.",
    "user_not_found": "Користувач не знайдений.",
    "invalid_command": "Формат: /send <user_id> <повідомлення>.",
    "error_occurred": "Сталася помилка. Зверніться до підтримки з кодом:",
    "communication": "Спілкування:",
    "current_situation": "Поточна ситуація в прифронтовій зоні:\n1. Розташування бомбосховищ: ...\n2. Маршрути евакуації: ...\n3. Інші важливі дані: ...",
    "available_resources": "Доступні ресурси:\n1. Медична допомога: ...\n2. Психологічна підтримка: ...\n3. Правова допомога: ...",
    "safety_info": "Інформація про безпеку:\n1. Як залишатися в безпеці: ...\n2. Як уникати обстрілів: ...\n3. Як знайти бомбосховище: ...",
    "other_resources": "Інші ресурси:\n1. Карти: ...\n2. Новини: ...\n3. Погода: ...",
    "select_user_prompt": "Ви обрали {username}. Напишіть /send {user_id} <повідомлення> для зв'язку."
}
def get_trace_id(context: ContextTypes.DEFAULT_TYPE) -> str:
    """Отримати унікальний trace_id для поточного запиту."""
    if "trace_id" not in context.chat_data:
        context.chat_data["trace_id"] = str(uuid.uuid4())
    return context.chat_data["trace_id"]
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    trace_id = get_trace_id(context)
    user = update.message.from_user
    users[user.id] = user.username
    logger.info(f"[{trace_id}] User started bot: {user.username} ({user.id})")
    await update.message.reply_text(MESSAGES["start"])



async def communicate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    trace_id = get_trace_id(context)
    logger.info(f"[{trace_id}] Command: /communicate")
    keyboard = [
        [InlineKeyboardButton("Спілкуйтеся з іншими людьми в прифронтовій зоні", callback_data="show_users")],
        [InlineKeyboardButton("Спілкуйтеся з тими, хто підтримує", callback_data="support")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(MESSAGES["communication"], reply_markup=reply_markup)



async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    trace_id = get_trace_id(context)
    query = update.callback_query
    await query.answer()
    logger.info(f"[{trace_id}] Button pressed: {query.data}")

    if query.data == "show_users":
        if users:
            keyboard = [
                [InlineKeyboardButton(username, callback_data=f"chat_{user_id}")]
                for user_id, username in users.items()
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(MESSAGES["choose_user"], reply_markup=reply_markup)
        else:
            await query.edit_message_text(MESSAGES["no_users"])
    elif query.data == "support":
        await query.edit_message_text(MESSAGES["support_unavailable"])


async def chat_with_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    trace_id = get_trace_id(context)
    query = update.callback_query
    await query.answer()
    logger.info(f"[{trace_id}] chat_with_user invoked")

    user_id = int(query.data.split("_")[1])
    if user_id in users:
        await query.edit_message_text(
            MESSAGES["select_user_prompt"].format(username=users[user_id], user_id=user_id)
        )
    else:
        await query.edit_message_text(MESSAGES["user_not_found"])


async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    trace_id = get_trace_id(context)
    try:
        user_id = int(context.args[0])
        message_text = " ".join(context.args[1:])
        if user_id in users:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"Повідомлення від {update.message.from_user.username}: {message_text}",
            )
            logger.info(f"[{trace_id}] Message sent from {update.message.from_user.id} to {user_id}")
            await update.message.reply_text(MESSAGES["message_sent"])
        else:
            logger.warning(f"[{trace_id}] User {user_id} not found.")
            await update.message.reply_text(MESSAGES["user_not_found"])
    except (IndexError, ValueError) as e:
        error_id = uuid.uuid4()
        logger.error(
            f"[{trace_id} | {error_id}] send_message error: "
            f"args={context.args}, user={update.message.from_user.id}, error={e}"
        )
        await update.message.reply_text(
            f"{MESSAGES['invalid_command']}\nКод помилки: {error_id}"
        )

async def situation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    trace_id = get_trace_id(context)
    logger.info(f"[{trace_id}] Command: /situation")
    await update.message.reply_text(MESSAGES["current_situation"])


async def resources(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    trace_id = get_trace_id(context)
    logger.info(f"[{trace_id}] Command: /назва")
    await update.message.reply_text(MESSAGES["available_resources"])


async def safety(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    trace_id = get_trace_id(context)
    logger.info(f"[{trace_id}] Command: /назва")
    await update.message.reply_text(MESSAGES["safety_info"])


async def other(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    trace_id = get_trace_id(context)
    logger.info(f"[{trace_id}] Command: /назва")
    await update.message.reply_text(MESSAGES["other_resources"])
def main() -> None:
    try:
        logger.info("Bot is starting...")
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
        logger.info("Bot is running.")

    except Exception as e:
        error_id = uuid.uuid4()
        logger.critical(f"[{error_id}] Critical error occurred!\n{traceback.format_exc()}")
        print(f"❌ {MESSAGES['error_occurred']} {error_id}")


if __name__ == "__main__":
    main()
