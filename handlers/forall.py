from telegram import Update
from telegram.ext import CallbackContext
import json
import os

USERS_FILE = "data/users.json"

def forall_command(update: Update, context: CallbackContext):
    # بررسی ادمین بودن
    admin_ids = list(map(int, os.getenv("ADMIN_IDS", "").split(',')))
    if update.effective_user.id not in admin_ids:
        update.message.reply_text("⛔ فقط ادمین‌ها می‌تونن پیام همگانی بفرستن.")
        return

    # بررسی اینکه پیام ریپلای شده یا نه
    if not update.message.reply_to_message:
        update.message.reply_text("❗ لطفاً این دستور رو روی یک پیام ریپلای کن.")
        return

    # بررسی وجود فایل کاربران
    if not os.path.exists(USERS_FILE):
        update.message.reply_text("❌ فایل کاربران پیدا نشد.")
        return

    # خواندن لیست کاربران
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)

    count = 0
    for user_id in users.keys():
        try:
            context.bot.copy_message(
                chat_id=int(user_id),
                from_chat_id=update.message.chat_id,
                message_id=update.message.reply_to_message.message_id
            )
            count += 1
        except Exception:
            continue

    update.message.reply_text(f"✅ پیام برای {count} نفر ارسال شد.")
