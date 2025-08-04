from telegram import Update
from telegram.ext import CallbackContext
from config import ADMIN_IDS
import json
import os

USERS_FILE = 'data/users.json'
ADMIN_FILE = 'data/admins.json'

def help_command(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return
    help_text = (
        "📋 راهنمای ادمین:\n\n"
        "/stats - مشاهده آمار کاربران\n"
        "/forall <متن> - ارسال پیام همگانی\n"
        "/addadmin <id> - افزودن ادمین جدید\n"
        "/removeadmin <id> - حذف ادمین\n"
        "/help - نمایش همین راهنما"
    )
    update.message.reply_text(help_text)

def stats_command(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if not os.path.exists(USERS_FILE):
        update.message.reply_text("هیچ کاربری یافت نشد.")
        return

    with open(USERS_FILE, 'r') as f:
        users = json.load(f)

    total = len(users)
    lines = [f"👥 تعداد کل کاربران: {total}\n"]
    for uid, info in users.items():
        name = info.get("name", "نامشخص")
        username = info.get("username", "ندارد")
        time = info.get("start_time", "")
        lines.append(f"👤 {name} (@{username}) - {uid} - {time}")

    msg = "\n".join(lines)
    update.message.reply_text(msg[:4000])

def forall_command(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return
    text = update.message.text.replace("/forall", "").strip()
    if not text:
        update.message.reply_text("متن پیام را وارد کنید.")
        return

    if not os.path.exists(USERS_FILE):
        update.message.reply_text("هیچ کاربری برای ارسال پیام نیست.")
        return

    with open(USERS_FILE, 'r') as f:
        users = json.load(f)

    for uid in users:
        try:
            context.bot.send_message(chat_id=int(uid), text=text)
        except:
            continue
    update.message.reply_text("✅ پیام برای همه کاربران ارسال شد.")

def add_admin(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if len(context.args) != 1:
        update.message.reply_text("مثال: /addadmin 123456789")
        return

    admin_id = int(context.args[0])
    if not os.path.exists(ADMIN_FILE):
        with open(ADMIN_FILE, 'w') as f:
            json.dump([], f)

    with open(ADMIN_FILE, 'r') as f:
        admins = json.load(f)

    if admin_id not in admins:
        admins.append(admin_id)
        with open(ADMIN_FILE, 'w') as f:
            json.dump(admins, f)
        update.message.reply_text("✅ ادمین جدید اضافه شد.")
    else:
        update.message.reply_text("این کاربر قبلاً ادمین شده.")

def remove_admin(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if len(context.args) != 1:
        update.message.reply_text("مثال: /removeadmin 123456789")
        return

    admin_id = int(context.args[0])
    if not os.path.exists(ADMIN_FILE):
        return

    with open(ADMIN_FILE, 'r') as f:
        admins = json.load(f)

    if admin_id in admins:
        admins.remove(admin_id)
        with open(ADMIN_FILE, 'w') as f:
            json.dump(admins, f)
        update.message.reply_text("✅ ادمین حذف شد.")
    else:
        update.message.reply_text("این آیدی ادمین نیست.")
