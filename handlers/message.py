from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from utils.helpers import save_new_user

def start_command(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("✉️ ارسال پیام به پشتیبانی", callback_data="start_message")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("سلام! چطوری؟ می‌تونی با زدن دکمه زیر پیام‌تو برامون بفرستی 💬", reply_markup=reply_markup)

def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.message.edit_text("لطفاً پیامت رو بنویس 😊\nوقتی نوشتی، همون لحظه برای ما ارسال میشه.")
    context.user_data["awaiting_message"] = True

def user_message(update: Update, context: CallbackContext):
    user = update.effective_user
    save_new_user(user)

    # فقط اگر کاربر در حالت ارسال پیام باشه
    if not context.user_data.get("awaiting_message"):
        return

    message = update.message
    context.user_data["awaiting_message"] = False

    from config import ADMIN_IDS
    for admin_id in ADMIN_IDS:
        try:
            context.bot.send_message(
                chat_id=admin_id,
                text=f"📩 پیام جدید از کاربر:\n\n👤 {user.full_name} (@{user.username})\n🆔 {user.id}\n\n💬 {message.text}"
            )
        except:
            pass

    message.reply_text("✅ پیامت با موفقیت برای پشتیبانی ارسال شد.")

def handle_reply_callback(update: Update, context: CallbackContext):
    pass  # اگر کدی اینجا داری، بزاریم جدا بررسی کنیم

def handle_block_unblock(update: Update, context: CallbackContext):
    pass  # اگر داری بفرست تا اصلاح کنم
