from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
from config import BOT_TOKEN, ADMIN_IDS
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
    remove_admin,
    handle_admin_reply
)

updater = Updater(token=BOT_TOKEN, use_context=True)
dp = updater.dispatcher

# دستورات اصلی
dp.add_handler(CommandHandler("start", start_command))
dp.add_handler(CallbackQueryHandler(button_callback, pattern="^start_message$"))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, user_message))

# پاسخ‌دهی ادمین
dp.add_handler(CallbackQueryHandler(handle_reply_callback, pattern="^reply:"))
dp.add_handler(MessageHandler(Filters.text & Filters.user(user_id=ADMIN_IDS), handle_admin_reply))

# بلاک و آنبلاک
dp.add_handler(CallbackQueryHandler(handle_block_unblock, pattern="^(block|unblock):"))

# دستورات ادمین
dp.add_handler(CommandHandler("stats", stats_command))
dp.add_handler(CommandHandler("help", help_command))
dp.add_handler(CommandHandler("forall", forall_command))
dp.add_handler(CommandHandler("addadmin", add_admin))
dp.add_handler(CommandHandler("removeadmin", remove_admin))

updater.start_polling()
updater.idle()
