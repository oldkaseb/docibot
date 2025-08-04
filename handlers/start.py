from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from utils.db import add_user

def start(update: Update, context: CallbackContext):
    user = update.effective_user
    add_user(user)

    text = (
        "سلام 👋\n"
        "به ربات رسمی دکتر گشاد خوش اومدی.\n"
        "پیامتو ارسال کن به گشادیم برسم زودی جوابتو میدم!"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✉️ ارسال پیام به گشاد", callback_data="send_msg")]
    ])

    update.message.reply_text(text, reply_markup=keyboard)

def send_button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.message.reply_text("✉️ حالا پیامتو بفرست!")

start_handler = CommandHandler("start", start)
send_button_handler = CallbackQueryHandler(send_button_handler, pattern="^send_msg$")
