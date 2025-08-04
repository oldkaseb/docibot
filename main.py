from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    Filters,
)
from config import BOT_TOKEN

# هندلرهای مربوط به شروع و دکمه ارسال پیام
from handlers.start import start_handler, send_button_callback

# هندلرهای مربوط به پیام و پاسخ‌دهی و بلاک
from handlers.message import (
    user_message_handler,
    reply_message_handler,
    button_callback_handler,
)

# هندلرهای ادمینی (help, stats, addadmin, deladmin)
from handlers.admin import handlers as admin_handlers

# هندلرهای ارسال پیام همگانی
from handlers.broadcast import forall_init_handler, handle_broadcast_message

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # 🟢 هندلرهای عمومی
    dp.add_handler(start_handler)                     # /start
    dp.add_handler(send_button_callback)             # دکمه "✉️ ارسال پیام"

    # 🟢 هندلر پیام کاربران و پاسخ ادمین‌ها
    dp.add_handler(user_message_handler)             # دریافت پیام کاربر
    dp.add_handler(reply_message_handler)            # پاسخ ادمین
    dp.add_handler(button_callback_handler)          # دکمه‌های ✉️ و 🔒

    # 🟢 پیام همگانی
    dp.add_handler(forall_init_handler)
    dp.add_handler(MessageHandler(
        Filters.private & ~Filters.command,
        handle_broadcast_message
    ))

    # 🟢 کامندهای مدیریتی (فقط برای ادمین‌ها)
    for handler in admin_handlers:
        dp.add_handler(handler)

    # 🚀 شروع ربات
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
