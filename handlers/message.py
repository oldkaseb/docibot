from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import os
import json

# بارگذاری لیست بلاک‌شده‌ها
def load_blocked_users():
    try:
        with open("data/blocked.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_blocked_users(blocked_users):
    with open("data/blocked.json", "w") as f:
        json.dump(blocked_users, f)

# متغیرهای محیطی
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))

# هندلر دکمه ارسال پیام به ادمین
def send_message_button(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.user_data['awaiting_message'] = True
    update.callback_query.answer()
    update.callback_query.message.delete()
    context.bot.send_message(chat_id=chat_id, text="✍ حالا پیامتو تایپ کن و بفرست تا دکتر گشاد ببینه...")

# هندلر پیام‌های کاربر
def user_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    username = update.effective_user.username or "نداره"
    name = update.effective_user.full_name
    text = update.message.text

    # چک بلاک
    blocked_users = load_blocked_users()
    if user_id in blocked_users:
        return

    if context.user_data.get('awaiting_message'):
        context.user_data['awaiting_message'] = False

        # ارسال پیام به همه ادمین‌ها
        for admin_id in ADMIN_IDS:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("✉️ پاسخ", callback_data=f"reply_{user_id}"),
                 InlineKeyboardButton("🔒 بلاک", callback_data=f"block_{user_id}")]
            ])
            context.bot.send_message(
                chat_id=admin_id,
                text=f"📨 پیام از {name} (@{username})\nID: {user_id}\n\n{text}",
                reply_markup=keyboard
            )

        # ارسال پیام تأیید به کاربر + دکمه ارسال مجدد
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="✅ ارسال شد!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✉️ ارسال پیام به دکتر گشاد", callback_data="send_message")]
            ])
        )
