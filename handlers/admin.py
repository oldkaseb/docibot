from telegram import Update
from telegram.ext import CallbackContext
import json
import os
from config import ADMIN_IDS

USERS_FILE = "data/users.json"
ADMINS_FILE = "data/admins.json"

# آمار کاربران
def stats_command(update: Update, context: CallbackContext):
    admin_ids = list(map(int, ADMIN_IDS.split(',')))
    if update.effective_user.id not in admin_ids:
        return

    if not os.path.exists(USERS_FILE):
        update.message.reply_text("❌ هیچ کاربری ثبت نشده.")
        return

    with open(USERS_FILE, 'r') as f:
        users = json.load(f)

    count = len(users)
    lines = [f"👥 مجموع کاربران: {count}\n\n"]
    for i, (uid, info) in enumerate(users.items(), 1):
        lines.append(f"{i}. {info['name']} ({info['username']})\n🆔 {uid} - ⏱ {info['start_time']}\n")

    message = "\n".join(lines)
    update.message.reply_text(message if len(message) < 4000 else message[:3900] + "\n...")

# راهنما
def help_command(update: Update, context: CallbackContext):
    admin_ids = list(map(int, ADMIN_IDS.split(',')))
    if update.effective_user.id not in admin_ids:
        return

    help_text = (
        "📘 راهنمای دستورات:\n\n"
        "/stats - مشاهده آمار کاربران\n"
        "/forall - ارسال پیام همگانی (ریپلای کنید)\n"
        "/addadmin [id] - افزودن ادمین\n"
        "/removeadmin [id] - حذف ادمین\n"
    )
    update.message.reply_text(help_text)

# پیام همگانی (در main جدا مدیریت می‌شه، اینجا صرفاً ارجاع داریم)
def forall_command(update: Update, context: CallbackContext):
    from handlers.forall import forall_command as real_forall
    return real_forall(update, context)

# افزودن ادمین
def add_admin(update: Update, context: CallbackContext):
    if update.effective_user.id not in list(map(int, ADMIN_IDS.split(','))):
        return

    if not context.args:
        update.message.reply_text("❗ لطفاً آیدی عددی ادمین جدید رو وارد کن.")
        return

    new_id = context.args[0]
    os.makedirs("data", exist_ok=True)
    if os.path.exists(ADMINS_FILE):
        with open(ADMINS_FILE, 'r') as f:
            admins = json.load(f)
    else:
        admins = []

    if new_id in admins:
        update.message.reply_text("⚠️ این کاربر از قبل ادمین هست.")
        return

    admins.append(new_id)
    with open(ADMINS_FILE, 'w') as f:
        json.dump(admins, f)

    update.message.reply_text(f"✅ ادمین جدید با آیدی {new_id} افزوده شد.")

# حذف ادمین
def remove_admin(update: Update, context: CallbackContext):
    if update.effective_user.id not in list(map(int, ADMIN_IDS.split(','))):
        return

    if not context.args:
        update.message.reply_text("❗ لطفاً آیدی عددی ادمین رو برای حذف وارد کن.")
        return

    remove_id = context.args[0]
    if os.path.exists(ADMINS_FILE):
        with open(ADMINS_FILE, 'r') as f:
            admins = json.load(f)
    else:
        admins = []

    if remove_id not in admins:
        update.message.reply_text("❌ این کاربر در لیست ادمین‌ها نیست.")
        return

    admins.remove(remove_id)
    with open(ADMINS_FILE, 'w') as f:
        json.dump(admins, f)

    update.message.reply_text(f"✅ ادمین با آیدی {remove_id} حذف شد.")
