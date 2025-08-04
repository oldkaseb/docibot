from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    Filters,
)
from config import BOT_TOKEN

# هندلرهای شروع و دکمه ارسال پیام
from handlers.start import start_handler, send_button_callback

# هندلرهای پیام، پاسخ، بلاک
from handlers.message import (
    user_message_handler,
    reply_message_handler,
    button_callback_handler,
)

# هندلرهای ادمین (help, stats, addadmin, deladmin)
from handlers.admin import handlers as admin_handlers

# هندلرهای پیام همگانی
from handlers.broadcast import forall_init_handler, handle_broadcast_message

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # 🟢 شروع و ارسال پیام
    dp.add_handler(start_handler)
    dp.add_handler(send_button_callback)

    # 🟢 پیام‌های کاربران و پاسخ ادمین
    dp.add_handler(user_message_handler)
    dp.add_handler(reply_message_handler)
    dp.add_handler(button_callback_handler)

    # 🟢 پیام همگانی
    dp.add_handler(forall_init_handler)
    dp.add_handler(MessageHandler(Filters.private & ~Filters.command, handle_broadcast_message))

    # 🟢 دستورات مدیریتی
    for handler in admin_handlers:
        dp.add_handler(handler)

    # 🚀 اجرای ربات
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
