from telegram import Update
from telegram.ext import CallbackContext
import json
import os
from datetime import datetime

USERS_FILE = 'data/users.json'
BROADCAST_FILE = 'data/broadcast.json'
ADMIN_IDS = [6041119040,7662192190]  # آیدی عددی ادمین‌ها اینجا قرار بگیره

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def is_admin(user_id):
    return user_id in ADMIN_IDS

def admin_command(update: Update, context: CallbackContext):
    if not is_admin(update.effective_user.id):
        return

    args = context.args
    if len(args) != 1 or not args[0].isdigit():
        update.message.reply_text("➕ برای افزودن ادمین، آیدی عددی رو وارد کن:\nمثال: /admin 123456789")
        return

    admin_id = int(args[0])
    if admin_id in ADMIN_IDS:
        update.message.reply_text("⚠️ این کاربر قبلاً ادمین بوده.")
    else:
        ADMIN_IDS.append(admin_id)
        update.message.reply_text(f"✅ آیدی {admin_id} به لیست ادمین‌ها اضافه شد.")

def remove_admin(update: Update, context: CallbackContext):
    if not is_admin(update.effective_user.id):
        return

    args = context.args
    if len(args) != 1 or not args[0].isdigit():
        update.message.reply_text("➖ برای حذف ادمین، آیدی عددی رو وارد کن:\nمثال: /removeadmin 123456789")
        return

    admin_id = int(args[0])
    if admin_id in ADMIN_IDS:
        ADMIN_IDS.remove(admin_id)
        update.message.reply_text(f"✅ آیدی {admin_id} از لیست ادمین‌ها حذف شد.")
    else:
        update.message.reply_text("❌ این آیدی داخل لیست ادمین‌ها نبود.")

def start_broadcast(update: Update, context: CallbackContext):
    if not is_admin(update.effective_user.id):
        return

    with open(BROADCAST_FILE, 'w') as f:
        json.dump({"active": True}, f)

    update.message.reply_text("📝 خب حالا گشاد بازی بسه\nپیام بعدی که می‌فرستی به همه کاربرها ارسال میشه.")

def handle_broadcast_message(update: Update, context: CallbackContext):
    if not is_admin(update.effective_user.id):
        return

    if not os.path.exists(BROADCAST_FILE):
        return

    with open(BROADCAST_FILE, 'r') as f:
        status = json.load(f)
    if not status.get("active"):
        return

    with open(BROADCAST_FILE, 'w') as f:
        json.dump({"active": False}, f)

    users = load_users()
    success = 0
    for user_id in users:
        try:
            context.bot.copy_message(chat_id=int(user_id),
                                     from_chat_id=update.effective_chat.id,
                                     message_id=update.message.message_id)
            success += 1
        except:
            continue
    update.message.reply_text(f"📣 پیام برای {success} کاربر ارسال شد.")

def show_stats(update: Update, context: CallbackContext):
    if not is_admin(update.effective_user.id):
        return

    users = load_users()
    if not users:
        update.message.reply_text("📊 آماری وجود ندارد.")
        return

    text = "📋 لیست کاربران:\n\n"
    for uid, data in users.items():
        name = data.get("name", "نامشخص")
        username = data.get("username", "-")
        time = data.get("time", "-")
        text += f"👤 {name} | @{username} | {uid}\n🕒 ورود: {time}\n\n"

    text += f"📈 مجموع کاربران: {len(users)}"
    update.message.reply_text(text)
