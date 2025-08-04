from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
import os
import json
from datetime import datetime

from handlers.admin import (
    add_admin,
    remove_admin,
    forall,
    handle_broadcast_message,
    stats,
    help_command
)
from handlers.message import user_message, start_command, button_callback

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(',')))
USERS_FILE = 'data/users.json'
BLOCK_FILE = 'data/blocked.json'

os.makedirs('data', exist_ok=True)
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as f:
        json.dump({}, f)

if not os.path.exists(BLOCK_FILE):
    with open(BLOCK_FILE, 'w') as f:
        json.dump([], f)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Command handlers
    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("admin", add_admin))
    dp.add_handler(CommandHandler("removeadmin", remove_admin))
    dp.add_handler(CommandHandler("forall", forall))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("help", help_command))

    # Message handlers
    dp.add_handler(MessageHandler(Filters.text & Filters.user(user_id=ADMIN_IDS), handle_broadcast_message))
    dp.add_handler(MessageHandler(Filters.private & ~Filters.command, user_message))
    dp.add_handler(CallbackQueryHandler(button_callback))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
