from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    Filters,
)
from config import BOT_TOKEN
from handlers.message import (
    start_command,
    button_callback,
    user_message,
    handle_reply_callback,
    handle_block_unblock,
    handle_admin_reply
)
from handlers.admin import (
    stats_command,
    help_command,
    forall_command,
    add_admin,
    remove_admin
)

def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # 🟢 دستورات کاربران
    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CallbackQueryHandler(button_callback, pattern="^start_message$"))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, user_message))

    # 🟢 پردازش دکمه پاسخ و بلاک/آنبلاک
    dp.add_handler(CallbackQueryHandler(handle_reply_callback, pattern="^reply:"))
    dp.add_handler(CallbackQueryHandler(handle_block_unblock, pattern="^(block|unblock):"))

    # 🟢 پاسخ‌گویی ادمین (حالت پاسخ فعال باشد)
    dp.add_handler(MessageHandler(Filters.text & Filters.reply, handle_admin_reply))

    # 🟢 دستورات ادمین
    dp.add_handler(CommandHandler("stats", stats_command))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("forall", forall_command))
    dp.add_handler(CommandHandler("addadmin", add_admin))
    dp.add_handler(CommandHandler("removeadmin", remove_admin))

    # ✅ شروع ربات
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
