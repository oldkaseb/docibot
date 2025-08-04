from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext
from utils.db import add_user

def start(update: Update, context: CallbackContext):
    user = update.effective_user
    add_user(user)
    text = "سلام 👋\nبه ربات رسمی دکتر گشاد خوش اومدی.\nپیامتو ارسال کن به گشادیم برسم زودی جوابتو میدم!"
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("✉️ ارسال پیام به گشاد", callback_data="send_msg")]])
    update.message.reply_text(text, reply_markup=keyboard)

start_handler = CommandHandler("start", start)