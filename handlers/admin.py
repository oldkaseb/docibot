from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import json
import os
from datetime import datetime

# مسیر ذخیره کاربران
USERS_FILE = 'data/users.json'

# متغیر محیطی برای آیدی ادمین‌ها (لیست)
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(',')))

# بررسی ادمین بودن
def is_admin(user_id):
    return user_id in ADMIN_IDS

# /admin - افزودن ادمین جدید
def add_admin(update: Update, context: CallbackContext):
    if not is_admin(update.effective_user.id):
        return
    try:
        new_admin_id = int(context.args[0])
        if new_admin_id not in ADMIN_IDS:
            ADMIN_IDS.append(new_admin_id)
            update.message.reply_text(f"✅ آیدی {new_admin_id} به لیست ادمین‌ها اضافه شد.")
        else:
            update.message.reply_text("این کاربر قبلاً ادمین بوده است.")
    except:
        update.message.reply_text("استفاده صحیح: /admin [user_id]")

# /removeadmin - حذف ادمین
def remove_admin(update: Update, context: CallbackContext):
    if not is_admin(update.effective_user.id):
        return
    try:
        remove_id = int(context.args[0])
        if remove_id in ADMIN_IDS:
            ADMIN_IDS.remove(remove_id)
            update.message.reply_text(f"❌ آیدی {remove_id} از لیست ادمین‌ها حذف شد.")
        else:
            update.message.reply_text("این کاربر ادمین نیست.")
    except:
        update.message.reply_text("استفاده صحیح: /removeadmin [user_id]")

# /forall - ارسال پیام همگانی
waiting_for_broadcast = {}

def forall(update: Update, context: CallbackContext):
    if not is_admin(update.effective_user.id):
        return
    waiting_for_broadcast[update.effective_user.id] = True
    update.message.reply_text("🗣 خب حالا گشاد بازی بسه. فور آل بزن ببینم چی میگی")

def handle_broadcast_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
    if waiting_for_broadcast.get(user_id):
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
        sent = 0
        for uid in users:
            try:
                context.bot.copy_message(chat_id=uid, from_chat_id=update.message.chat_id, message_id=update.message.message_id)
                sent += 1
            except:
                continue
        update.message.reply_text(f"📨 پیام به {sent} کاربر ارسال شد.")
        waiting_for_broadcast.pop(user_id)

# /stats - نمایش آمار ربات
def stats(update: Update, context: CallbackContext):
    if not is_admin(update.effective_user.id):
        return
    try:
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
        if not users:
            update.message.reply_text("🔢 هیچ کاربری ثبت نشده است.")
            return
        text = "📊 لیست کاربران ثبت‌شده:\n\n"
        for i, (uid, info) in enumerate(users.items(), 1):
            name = info.get('name', '-')
            username = info.get('username', '-')
            time = info.get('time', '-')
            text += f"{i}. {name} | @{username} | {uid} | {time}\n"
        text += f"\n📌 مجموع کاربران: {len(users)}"
        update.message.reply_text(text)
    except:
        update.message.reply_text("❌ خطا در خواندن فایل کاربران.")

# /help - راهنما
help_text = """
🆘 راهنمای دستورات:

1️⃣ /admin [id] ➤ افزودن ادمین جدید
2️⃣ /removeadmin [id] ➤ حذف ادمین
3️⃣ /forall ➤ پیام همگانی
4️⃣ /stats ➤ آمار کاربران
5️⃣ ارسال پیام ➤ با دکمه ارسال پیام
"""

def help_command(update: Update, context: CallbackContext):
    if not is_admin(update.effective_user.id):
        return
    update.message.reply_text(help_text)
