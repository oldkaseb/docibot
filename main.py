import os
import logging
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram import BotCommand
from handlers.admin import (
    add_admin, remove_admin, broadcast_entry, broadcast_message,
    show_stats, show_help, handle_admin_response, handle_block_unblock
)
from handlers.message import (
    start_command, user_message_handler, show_main_menu,
    prompt_for_message, cancel_message_input
)
from dotenv import load_dotenv

load_dotenv()

# تنظیم لاگر
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# گرفتن توکن و ادمین‌ها از محیط
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    # دستورات ادمینی
    dp.add_handler(CommandHandler("admin", add_admin))
    dp.add_handler(CommandHandler("removeadmin", remove_admin))
    dp.add_handler(CommandHandler("forall", broadcast_entry))
    dp.add_handler(MessageHandler(Filters.text & Filters.chat(ADMIN_IDS), broadcast_message))
    dp.add_handler(CommandHandler("stats", show_stats))
    dp.add_handler(CommandHandler("help", show_help))

    # پیام‌های ورودی کاربر
    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CallbackQueryHandler(prompt_for_message, pattern="^send_message$"))
    dp.add_handler(CallbackQueryHandler(cancel_message_input, pattern="^cancel_send$"))
    dp.add_handler(CallbackQueryHandler(handle_admin_response, pattern="^reply:"))
    dp.add_handler(CallbackQueryHandler(handle_block_unblock, pattern="^(block|unblock):"))

    # هندل پیام‌های خصوصی کاربران (غیردستور)
    dp.add_handler(MessageHandler(Filters.private & ~Filters.command, user_message_handler))

    # اجرای ربات
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
