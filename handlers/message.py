from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext
import json
import os
from datetime import datetime
from config import ADMIN_IDS

USERS_FILE = 'data/users.json'
BLOCK_FILE = 'data/blocked.json'
REPLY_STATE_FILE = 'data/reply_state.json'

os.makedirs('data', exist_ok=True)
for file in [USERS_FILE, BLOCK_FILE, REPLY_STATE_FILE]:
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump({} if "users" in file else [], f)

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f)

def start_command(update: Update, context: CallbackContext):
    user = update.effective_user
    user_data = {
        "name": user.full_name,
        "username": user.username or "—",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    users = load_json(USERS_FILE)
    users[str(user.id)] = user_data
    save_json(USERS_FILE, users)

    keyboard = [[InlineKeyboardButton("✉️ ارسال پیام به پشتیبانی", callback_data="send_message")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        "سلام! برای ارسال پیام به پشتیبانی، روی دکمه زیر کلیک کنید:",
        reply_markup=reply_markup
    )

def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    user_id = query.from_user.id
    blocked_users = load_json(BLOCK_FILE)

    if query.data == "send_message":
        if user_id in blocked_users:
            query.edit_message_text("⛔ شما بلاک شده‌اید.")
            return
        context.user_data["awaiting_message"] = True
        query.edit_message_text("✍️ لطفاً پیام خود را بنویسید و ارسال کنید.")
    elif query.data.startswith("reply_"):
        target_id = int(query.data.split("_")[1])
        reply_state = load_json(REPLY_STATE_FILE)
        reply_state[str(query.from_user.id)] = target_id
        save_json(REPLY_STATE_FILE, reply_state)
        query.answer("منتظر دریافت پیام شما برای کاربر هستم.")
    elif query.data.startswith("block_"):
        target_id = int(query.data.split("_")[1])
        blocked = load_json(BLOCK_FILE)
        if target_id not in blocked:
            blocked.append(target_id)
            save_json(BLOCK_FILE, blocked)
        query.answer("✅ کاربر بلاک شد.")
    elif query.data.startswith("unblock_"):
        target_id = int(query.data.split("_")[1])
        blocked = load_json(BLOCK_FILE)
        if target_id in blocked:
            blocked.remove(target_id)
            save_json(BLOCK_FILE, blocked)
        query.answer("✅ کاربر آنبلاک شد.")

def user_message(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = user.id
    text = update.message.text
    blocked_users = load_json(BLOCK_FILE)

    if user_id in blocked_users:
        update.message.reply_text("⛔ شما بلاک شده‌اید.")
        return

    if context.user_data.get("awaiting_message"):
        for admin_id in ADMIN_IDS:
            keyboard = [
                [
                    InlineKeyboardButton("✉️ پاسخ", callback_data=f"reply_{user_id}"),
                    InlineKeyboardButton("🚫 بلاک", callback_data=f"block_{user_id}")
                ]
            ]
            markup = InlineKeyboardMarkup(keyboard)
            try:
                context.bot.send_message(
                    chat_id=admin_id,
                    text=f"📩 پیام جدید از {user.full_name} (@{user.username or 'ندارد'})\n\n{update.message.text}",
                    reply_markup=markup
                )
            except:
                pass

        context.user_data["awaiting_message"] = False
        update.message.reply_text("✅ پیام شما ارسال شد.")
        return

    # پاسخ ادمین به کاربر
    reply_state = load_json(REPLY_STATE_FILE)
    sender_id = str(user_id)

    if sender_id in reply_state:
        target_id = reply_state[sender_id]
        try:
            context.bot.send_message(chat_id=target_id, text=text)
            update.message.reply_text("✅ پیام شما ارسال شد.")
        except:
            update.message.reply_text("❗ ارسال پیام به کاربر ناموفق بود.")
        del reply_state[sender_id]
        save_json(REPLY_STATE_FILE, reply_state)
