from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext
from utils.db import add_user

# /start handler
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    add_user(user)

    text = (
        "سلام 👋\n"
        "به ربات رسمی دکتر گشاد خوش اومدی.\n"
        "پیامتو ارسال کن به گشادیم برسم زودی جوابتو میدم!"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✉️ ارسال پیام به دکتر گشاد", callback_data="send_msg")]
    ])

    update.message.reply_text(text, reply_markup=keyboard)

# handler برای کلیک روی دکمه
def send_button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.message.reply_text("✉️ حالا می‌تونی پیامتو برای دکتر گشاد بفرستی... منتظرم!")

# خروجی هندلرها
start_handler = CommandHandler("start", start)
send_button_callback = CallbackQueryHandler(send_button_handler, pattern="^send_msg$")
