from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import os
import json
from datetime import datetime

# 🔒 متغیرهای محیطی
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()]

# 🗂 مسیر فایل آمار
USER_DATA_FILE = "users.json"

# 📥 هندلر شروع
def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "-"
    full_name = update.message.from_user.full_name

    # ذخیره کاربر
    save_user(user_id, username, full_name)

    keyboard = [[InlineKeyboardButton("✉️ ارسال پیام به دکتر گشاد", callback_data="send_message")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        "سلام 👋\n"
        "به ربات رسمی دکتر گشاد خوش اومدی.\n"
        "پیامتو ارسال کن، به گشادیم برسون، زودی جوابتو میدیم!",
        reply_markup=reply_markup
    )

# 💾 ذخیره اطلاعات کاربر در فایل
def save_user(user_id, username, full_name):
    if not os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'w') as f:
            json.dump({}, f)

    with open(USER_DATA_FILE, 'r') as f:
        data = json.load(f)

    if str(user_id) not in data:
        data[str(user_id)] = {
            "username": username,
            "name": full_name,
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)

# 🎯 هندلر کلیک روی دکمه "ارسال پیام"
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "send_message":
        context.user_data["awaiting_message"] = True
        query.edit_message_text("✍ حالا پیامتو تایپ کن و بفرست تا دکتر گشاد ببینه...")

# 📨 وقتی کاربر پیام می‌فرسته
def user_message(update: Update, context: CallbackContext):
    if context.user_data.get("awaiting_message"):
        message = update.message.text

        # ارسال به همه ادمین‌ها
        keyboard = [
            [
                InlineKeyboardButton("✉️ پاسخ", callback_data=f"reply_{update.message.chat.id}"),
                InlineKeyboardButton("بلاک 🔒", callback_data=f"block_{update.message.chat.id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        for admin_id in ADMIN_IDS:
            context.bot.send_message(
                chat_id=admin_id,
                text=(
                    f"📨 پیام از: {update.message.from_user.full_name} "
                    f"(@{update.message.from_user.username or 'نداره'})\n"
                    f"ID: {update.message.from_user.id}\n\n"
                    f"{message}"
                ),
                reply_markup=reply_markup
            )

        # تایید برای کاربر
        update.message.reply_text("✅ پیامت ارسال شد! دکتر گشاد به‌زودی جوابتو میده.")
        context.user_data["awaiting_message"] = False
    else:
        update.message.reply_text("اول باید روی دکمه ✉️ ارسال پیام کلیک کنی.")

# 🆘 راهنما
def help_command(update: Update, context: CallbackContext):
    update.message.reply_text("📌 راهنما:\n/start - شروع ربات\n/help - همین پیام")

# 🔁 دریافت کلیک پاسخ ادمین (در نسخه پیشرفته فعال میشه)
def admin_buttons(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_reply_markup(reply_markup=None)
    query.message.reply_text("🚧 قابلیت پاسخ و بلاک در حال توسعه است.")

# 🚀 اجرای ربات
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CallbackQueryHandler(button, pattern="^send_message$"))
    dp.add_handler(CallbackQueryHandler(admin_buttons, pattern="^(reply_|block_)"))
    dp.add_handler(MessageHandler(Filters.text & Filters.private, user_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
