from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext
from utils.db import add_user

def start(update: Update, context: CallbackContext):
    user = update.effective_user
    add_user(user)
    text = "سلام 👋\nبه ربات رسمی دکتر گشاد خوش اومدی.\nپیامتو ارسال کن به گشادیم برسم زودی جوابتو میدم!"
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("✉️ ارسال پیام به دکتر گشاد", callback_data="send_msg")]])
    update.message.reply_text(text, reply_markup=keyboard)

def send_button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_reply_markup(reply_markup=None)
    query.message.reply_text("✍️ حالا پیامتو تایپ کن و بفرست تا دکتر گشاد ببینه...")

start_handler = CommandHandler("start", start)
send_button_callback = CallbackQueryHandler(send_button_handler, pattern="^send_msg$")
