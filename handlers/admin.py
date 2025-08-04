from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext
import json
import os
from datetime import datetime

DATA_FOLDER = 'data'
USERS_FILE = os.path.join(DATA_FOLDER, 'users.json')
BLOCK_FILE = os.path.join(DATA_FOLDER, 'blocked.json')
ADMINS_FILE = os.path.join(DATA_FOLDER, 'admins.json')

if not os.path.exists(ADMINS_FILE):
    with open(ADMINS_FILE, 'w') as f:
        json.dump([], f)

with open(ADMINS_FILE, 'r') as f:
    extra_admins = json.load(f)

ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(',')))
ALL_ADMINS = ADMIN_IDS + extra_admins

def start_command(update: Update, context: CallbackContext):
    user = update.effective_user
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    if str(user.id) not in users:
        users[str(user.id)] = {
            "name": user.full_name,
            "username": user.username,
            "joined": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)

    keyboard = [[InlineKeyboardButton("✉️ ارسال پیام به پشتیبانی", callback_data='send_message')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "به ربات خوش آمدید!\nبرای ارسال پیام به پشتیبانی روی دکمه زیر کلیک کنید:",
        reply_markup=reply_markup
    )

def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    query.answer()

    if data == "send_message":
        context.user_data['awaiting_message'] = True
        query.edit_message_text("پیام خود را بنویسید و برای ما ارسال کنید:")

    elif data.startswith("reply_") and user_id in ALL_ADMINS:
        target_user_id = int(data.split("_")[1])
        context.user_data['reply_to'] = target_user_id
        query.message.reply_text("لطفاً پاسخ خود را ارسال کنید:", reply_markup=ReplyKeyboardRemove())

    elif data.startswith("block_") and user_id in ALL_ADMINS:
        target_user_id = int(data.split("_")[1])
        with open(BLOCK_FILE, 'r') as f:
            blocked_users = json.load(f)
        if target_user_id not in blocked_users:
            blocked_users.append(target_user_id)
            with open(BLOCK_FILE, 'w') as f:
                json.dump(blocked_users, f)
        query.message.reply_text("کاربر بلاک شد ✅")

    elif data.startswith("unblock_") and user_id in ALL_ADMINS:
        target_user_id = int(data.split("_")[1])
        with open(BLOCK_FILE, 'r') as f:
            blocked_users = json.load(f)
        if target_user_id in blocked_users:
            blocked_users.remove(target_user_id)
            with open(BLOCK_FILE, 'w') as f:
                json.dump(blocked_users, f)
        query.message.reply_text("کاربر آنبلاک شد ✅")

def user_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    text = update.message.text

    with open(BLOCK_FILE, 'r') as f:
        blocked_users = json.load(f)
    if user_id in blocked_users:
        return

    if context.user_data.get('awaiting_message'):
        context.user_data['awaiting_message'] = False
        update.message.reply_text("✅ پیام شما ارسال شد. منتظر پاسخ بمانید.")
        for admin_id in ALL_ADMINS:
            try:
                keyboard = [
                    [
                        InlineKeyboardButton("✉️ پاسخ", callback_data=f"reply_{user_id}"),
                        InlineKeyboardButton("❌ بلاک", callback_data=f"block_{user_id}"),
                        InlineKeyboardButton("✅ آنبلاک", callback_data=f"unblock_{user_id}")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                context.bot.send_message(
                    chat_id=admin_id,
                    text=f"📩 پیام جدید از کاربر:
👤 {update.effective_user.full_name} (@{update.effective_user.username})
🆔 {user_id}

📝 {text}",
                    reply_markup=reply_markup
                )
            except:
                pass

    elif 'reply_to' in context.user_data:
        target_user_id = context.user_data['reply_to']
        try:
            context.bot.send_message(chat_id=target_user_id, text=f"📬 پاسخ پشتیبانی:
{text}")
            update.message.reply_text("✅ پاسخ شما ارسال شد.")
        except:
            update.message.reply_text("❌ خطا در ارسال پاسخ. ممکن است کاربر ربات را بلاک کرده باشد.")
        context.user_data.pop('reply_to', None)
    else:
        update.message.reply_text("برای ارسال پیام، ابتدا روی دکمه ارسال پیام کلیک کنید.")
