from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from config import ADMIN_IDS
from utils.db import get_all_users
import json

admins = set(ADMIN_IDS)

def help_command(update: Update, context: CallbackContext):
    if update.effective_user.id not in admins:
        return
    help_text = ("🧾 <b>دستورات مدیریت ربات</b>:\n\n"
                 "➕ /addadmin [user_id] - افزودن ادمین جدید\n"
                 "➖ /deladmin [user_id] - حذف ادمین\n"
                 "📊 /stats - آمار کاربران\n"
                 "📢 /forall - پیام همگانی\n"
                 "🆘 /help - راهنما\n")
    update.message.reply_text(help_text, parse_mode="HTML")

def addadmin(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_IDS[0]:
        return update.message.reply_text("فقط ادمین اصلی اجازه دارد!")
    if len(context.args) != 1:
        return update.message.reply_text("استفاده صحیح: /addadmin [user_id]")
    try:
        new_admin = int(context.args[0])
        admins.add(new_admin)
        update.message.reply_text("✅ ادمین جدید افزوده شد.")
    except:
        update.message.reply_text("خطا در افزودن ادمین.")

def deladmin(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_IDS[0]:
        return update.message.reply_text("فقط ادمین اصلی اجازه دارد!")
    if len(context.args) != 1:
        return update.message.reply_text("استفاده صحیح: /deladmin [user_id]")
    try:
        del_admin = int(context.args[0])
        if del_admin == ADMIN_IDS[0]:
            return update.message.reply_text("نمی‌تونی ادمین اصلی رو حذف کنی!")
        admins.discard(del_admin)
        update.message.reply_text("✅ ادمین حذف شد.")
    except:
        update.message.reply_text("خطا در حذف ادمین.")

def stats(update: Update, context: CallbackContext):
    if update.effective_user.id not in admins:
        return
    users = get_all_users()
    total = len(users)
    text = f"📊 <b>آمار کاربران:</b> (تعداد کل: {total})\n\n"
    for user in users.values():
        text += (f"👤 {user['full_name']} (@{user['username']})\n"
                 f"🆔 <code>{user['id']}</code>\n"
                 f"🕐 ورود: {user['joined_at']}\n\n")
    if len(text) > 4000:
        update.message.reply_document(document=bytes(json.dumps(users, indent=2, ensure_ascii=False), "utf-8"), filename="users.json")
    else:
        update.message.reply_text(text, parse_mode="HTML")

handlers = [
    CommandHandler("help", help_command),
    CommandHandler("addadmin", addadmin),
    CommandHandler("deladmin", deladmin),
    CommandHandler("stats", stats),
]