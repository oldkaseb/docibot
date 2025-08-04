from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from config import ADMIN_IDS
from utils.db import (
    get_all_users,
    get_blocked_users,
    add_admin_id,
    remove_admin_id,
    is_admin,
    block_user,
    unblock_user,
    is_blocked
)
from utils.helpers import broadcast
import json
from datetime import datetime


def stats_command(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return
    users = get_all_users()
    text = f"📊 آمار کاربران:\n\n👤 تعداد کل: {len(users)}\n"
    for uid, info in users.items():
        name = info.get("name", "—")
        username = info.get("username", "—")
        time = info.get("time", "—")
        text += f"\n🆔 {uid}\n👤 {name} | @{username}\n🕰 {time}\n"
    update.message.reply_text(text)


def help_command(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return
    text = "📖 راهنمای ادمین:\n\n"
    text += "/stats - آمار کاربران\n"
    text += "/forall - پیام همگانی (با ریپلای)\n"
    text += "/addadmin [id] - افزودن ادمین\n"
    text += "/removeadmin [id] - حذف ادمین\n"
    update.message.reply_text(text)


def forall_command(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return update.message.reply_text("⛔ فقط ادمین‌ها می‌تونن پیام همگانی بفرستن.")
    if not update.message.reply_to_message:
        return update.message.reply_text("❗ باید روی یک پیام ریپلای کنید.")
    success, fail = broadcast(context.bot, update.message.reply_to_message)
    update.message.reply_text(f"✅ ارسال شد: {success}\n❌ شکست‌خورده: {fail}")


def add_admin(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if len(context.args) != 1:
        return update.message.reply_text("❗ لطفاً یک آیدی عددی وارد کنید.")
    try:
        admin_id = int(context.args[0])
        add_admin_id(admin_id)
        update.message.reply_text(f"✅ ادمین {admin_id} اضافه شد.")
    except:
        update.message.reply_text("⛔ آیدی وارد شده معتبر نیست.")


def remove_admin(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if len(context.args) != 1:
        return update.message.reply_text("❗ لطفاً یک آیدی عددی وارد کنید.")
    try:
        admin_id = int(context.args[0])
        remove_admin_id(admin_id)
        update.message.reply_text(f"✅ ادمین {admin_id} حذف شد.")
    except:
        update.message.reply_text("⛔ آیدی وارد شده معتبر نیست.")


def handle_reply_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data.split(":")
    if len(data) != 2:
        return
    _, user_id = data
    context.user_data["reply_to"] = int(user_id)
    query.message.reply_text("✉️ لطفاً پاسخ خود را ارسال کنید.")


def handle_admin_reply(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return
    reply_to = context.user_data.get("reply_to")
    if not reply_to:
        return
    try:
        context.bot.send_message(chat_id=reply_to, text=update.message.text)
        update.message.reply_text("✅ پیام شما ارسال شد.")
    except:
        update.message.reply_text("❌ ارسال پیام ناموفق بود.")
    context.user_data["reply_to"] = None


def handle_block_unblock(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data.split(":")
    if len(data) != 2:
        return
    action, user_id = data
    user_id = int(user_id)

    if update.effective_user.id not in ADMIN_IDS:
        return

    if action == "block":
        block_user(user_id)
        query.edit_message_text("❌ کاربر بلاک شد.")
    elif action == "unblock":
        unblock_user(user_id)
        query.edit_message_text("✅ کاربر آزاد شد.")
