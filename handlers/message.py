from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import json
import os
from config import ADMIN_IDS

USERS_FILE = "data/users.json"
BLOCKED_FILE = "data/blocked.json"
REPLY_STATE_FILE = "data/reply_state.json"

# شروع ربات
def start_command(update: Update, context: CallbackContext):
    user = update.effective_user
    user_data = {
        "id": user.id,
        "name": f"{user.first_name} {user.last_name or ''}".strip(),
        "username": f"@{user.username}" if user.username else "ندارد",
        "start_time": str(update.message.date)
    }

    os.makedirs("data", exist_ok=True)
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
    else:
        users = {}

    if str(user.id) not in users:
        users[str(user.id)] = user_data
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f)

    keyboard = InlineKeyboardMarkup.from_button(
        InlineKeyboardButton("✉️ پیام دادن به پشتیبانی", callback_data="start_message")
    )
    update.message.reply_text(
        "👋 خوش آمدی عزیز!\n\nبرای ارسال پیام به پشتیبانی، دکمه زیر رو بزن.",
        reply_markup=keyboard
    )

# دکمه شروع ارسال پیام
def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    keyboard = InlineKeyboardMarkup.from_button(
        InlineKeyboardButton("📨 ارسال مجدد پیام", callback_data="start_message")
    )
    query.edit_message_text(
        "✍️ حالا پیامت رو بفرست. منتظرم...",
        reply_markup=None
    )
    return

# ارسال پیام کاربر به ادمین‌ها
def user_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    # بررسی بلاک بودن
    if os.path.exists(BLOCKED_FILE):
        with open(BLOCKED_FILE, 'r') as f:
            blocked = json.load(f)
        if str(user_id) in blocked:
            return

    text = update.message.text
    user = update.effective_user

    for admin_id in map(int, ADMIN_IDS.split(',')):
        context.bot.send_message(
            chat_id=admin_id,
            text=f"📩 پیام جدید از کاربر:\n\n👤 {user.first_name} ({user.username or 'ندارد'})\n🆔 {user.id}\n\n📝 {text}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✉️ پاسخ", callback_data=f"reply:{user.id}")],
                [InlineKeyboardButton("🚫 بلاک", callback_data=f"block:{user.id}")]
            ])
        )

    update.message.reply_text("✅ پیامت ارسال شد. منتظر پاسخ باش عزیز.")

# ثبت حالت پاسخ برای ادمین
def handle_reply_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    user_id = query.data.split(":")[1]

    with open(REPLY_STATE_FILE, 'w') as f:
        json.dump({"user_id": user_id}, f)

    query.edit_message_text("✍️ پیام‌تو بفرست تا برای کاربر ارسال کنم...")

# ارسال پاسخ ادمین به کاربر
def handle_admin_reply(update: Update, context: CallbackContext):
    if not os.path.exists(REPLY_STATE_FILE):
        update.message.reply_text("❌ هیچ درخواستی برای پاسخ یافت نشد.")
        return

    with open(REPLY_STATE_FILE, 'r') as f:
        reply_state = json.load(f)

    user_id = int(reply_state["user_id"])
    text = update.message.text

    try:
        context.bot.send_message(chat_id=user_id, text=f"📬 پاسخ پشتیبانی:\n\n{text}")
        update.message.reply_text("✅ پاسخ برای کاربر ارسال شد.")
    except Exception as e:
        update.message.reply_text("❌ ارسال پیام به کاربر ناموفق بود.")
    
    os.remove(REPLY_STATE_FILE)

# بلاک و آنبلاک
def handle_block_unblock(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data.split(":")
    action = data[0]
    user_id = data[1]

    os.makedirs("data", exist_ok=True)

    if os.path.exists(BLOCKED_FILE):
        with open(BLOCKED_FILE, 'r') as f:
            blocked = json.load(f)
    else:
        blocked = {}

    if action == "block":
        blocked[user_id] = True
        with open(BLOCKED_FILE, 'w') as f:
            json.dump(blocked, f)
        query.edit_message_reply_markup(InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ آنبلاک", callback_data=f"unblock:{user_id}")]
        ]))
        query.edit_message_text("❌ کاربر بلاک شد.")
    elif action == "unblock":
        if user_id in blocked:
            blocked.pop(user_id)
            with open(BLOCKED_FILE, 'w') as f:
                json.dump(blocked, f)
        query.edit_message_text("✅ کاربر آنبلاک شد.")
