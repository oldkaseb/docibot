from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters, CallbackContext
from config import BOT_TOKEN, ADMIN_IDS
from handlers.forall import forall_command
from handlers.message import (
    start_command,
    button_callback,
    user_message,
    handle_reply_callback,
    handle_block_unblock
)
from handlers.admin import (
    stats_command,
    help_command,
    forall_command,
    add_admin,
    remove_admin
)

# شروع ربات
updater = Updater(token=BOT_TOKEN, use_context=True)
dp = updater.dispatcher

# دستورات کاربری
dp.add_handler(CommandHandler("start", start_command))
dp.add_handler(CommandHandler("forall", forall_command))
dp.add_handler(CallbackQueryHandler(button_callback, pattern="^start_message$"))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, user_message))

# پاسخ ادمین به کاربران (محدود به ادمین‌های تعریف‌شده)
dp.add_handler(CallbackQueryHandler(handle_reply_callback, pattern="^reply:"))
dp.add_handler(MessageHandler(
    Filters.text & Filters.user(user_id=[int(i) for i in ADMIN_IDS.split(',')]),
    handle_admin_reply
))

# بلاک و آنبلاک
dp.add_handler(CallbackQueryHandler(handle_block_unblock, pattern="^(block|unblock):"))

# دستورات ویژه ادمین
dp.add_handler(CommandHandler("stats", stats_command))
dp.add_handler(CommandHandler("help", help_command))
dp.add_handler(CommandHandler("forall", forall_command))
dp.add_handler(CommandHandler("addadmin", add_admin))
dp.add_handler(CommandHandler("removeadmin", remove_admin))

# اجرای ربات
updater.start_polling()
updater.idle()
