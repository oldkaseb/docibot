from telegram import Update
from telegram.ext import CallbackContext
import json
import os
from datetime import datetime
from config import ADMIN_IDS

ADMIN_FILE = 'data/admins.json'
USER_FILE = 'data/users.json'

# ایجاد فایل اگر وجود نداشت
os.makedirs('data', exist_ok=True)
if not os.path.exists(ADMIN_FILE):
    with open(ADMIN_FILE, 'w') as f:
        json.dump(ADMIN_IDS, f)

def save_admins(admins):
    with open(ADMIN_FILE, 'w') as f:
        json.dump(admins, f)

def load_admins():
    with open(ADMIN_FILE, 'r') as f:
        return json.load(f)

def add_admin(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    admins = load_admins()
    
    if user_id not in ADMIN_IDS:
        update.message.reply_text("⛔ شما اجازه افزودن ادمین را ندارید.")
        return

    if len(context.args) != 1:
        update.message.reply_text("❗ فرمت درست نیست. لطفا به صورت زیر بنویسید:\n/admin 123456789")
        return

    new_admin = int(context.args[0])
    if new_admin in admins:
        update.message.reply_text("ℹ️ این کاربر از قبل ادمین است.")
    else:
        admins.append(new_admin)
        save_admins(admins)
        update.message.reply_text(f"✅ کاربر {new_admin} با موفقیت به لیست ادمین‌ها اضافه شد.")

def remove_admin(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    admins = load_admins()

    if user_id not in ADMIN_IDS:
        update.message.reply_text("⛔ شما اجازه حذف ادمین را ندارید.")
        return

    if len(context.args) != 1:
        update.message.reply_text("❗ فرمت درست نیست. لطفا به صورت زیر بنویسید:\n/removeadmin 123456789")
        return

    target_admin = int(context.args[0])
    if target_admin not in admins:
        update.message.reply_text("❗ این کاربر در لیست ادمین‌ها نیست.")
    else:
        if target_admin in ADMIN_IDS:
            update.message.reply_text("⚠️ شما نمی‌توانید ادمین‌های اصلی ثبت‌شده در متغیرها را حذف کنید.")
            return
        admins.remove(target_admin)
        save_admins(admins)
        update.message.reply_text(f"🗑️ کاربر {target_admin} از لیست ادمین‌ها حذف شد.")

def help_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in load_admins():
        return

    help_text = (
        "📘 راهنمای ادمین:\n\n"
        "1. /admin <id> ➤ افزودن ادمین\n"
        "2. /removeadmin <id> ➤ حذف ادمین\n"
        "3. /forall ➤ ارسال پیام همگانی\n"
        "4. /stats ➤ نمایش آمار کاربران\n"
        "5. /help ➤ راهنمای دستورات ادمین"
    )
    update.message.reply_text(help_text)

def forall(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in load_admins():
        update.message.reply_text("⛔ شما ادمین نیستید.")
        return

    context.user_data['awaiting_broadcast'] = True
    update.message.reply_text("✉️ پیام خود را ارسال کنید تا به همه کاربران فرستاده شود.")

def handle_broadcast_message(update: Update, context: CallbackContext):
    if not context.user_data.get('awaiting_broadcast'):
        return

    with open(USER_FILE, 'r') as f:
        users = json.load(f)

    sent = 0
    for uid in users:
        try:
            context.bot.send_message(chat_id=int(uid), text=update.message.text)
            sent += 1
        except:
            continue

    update.message.reply_text(f"📤 پیام شما به {sent} کاربر ارسال شد.")
    context.user_data['awaiting_broadcast'] = False

def stats(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in load_admins():
        update.message.reply_text("⛔ شما ادمین نیستید.")
        return

    if not os.path.exists(USER_FILE):
        update.message.reply_text("❗ فایل کاربران یافت نشد.")
        return

    with open(USER_FILE, 'r') as f:
        users = json.load(f)

    if not users:
        update.message.reply_text("هیچ کاربری ثبت نشده است.")
        return

    message = f"📊 آمار کاربران ({len(users)} نفر):\n\n"
    for uid, data in users.items():
        name = data.get("name", "—")
        username = data.get("username", "—")
        date = data.get("date", "—")
        message += f"👤 {name} | @{username} | {uid}\n🕒 {date}\n\n"

    update.message.reply_text(message)
