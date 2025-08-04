from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext
import os
import json
from datetime import datetime
from config import ADMIN_IDS

USERS_FILE = 'data/users.json'
BLOCK_FILE = 'data/blocked.json'
REPLY_STATE_FILE = 'data/reply_state.json'

def start_command(update: Update, context: CallbackContext):
    user = update.effective_user
    os.makedirs('data', exist_ok=True)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)

    with open(USERS_FILE, 'r') as f:
        users = json.load(f)

    if str(user.id) not in users:
        users[str(user.id)] = {
            "name": user.full_name,
            "username": user.username,
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📨 فرستادن پیام به دکتر گشاد", callback_data="start_message")]
    ])

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="سلام! 👋\nمی‌تونی یه پیام واسه دکتر گشاد بفرستی. روی دکمه زیر بزن و تایپ کن 😎👇",
        reply_markup=keyboard
    )

def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if query.data == "start_message":
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text="✍️ حالا پیامتو بنویس و بفرست. هر وقت خواستی می‌تونی دوباره پیام بدی 😄",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["waiting_for_message"] = True

def user_message(update: Update, context: CallbackContext):
    user = update.effective_user
    text = update.message.text
    if not context.user_data.get("waiting_for_message"):
        return

    if os.path.exists(BLOCK_FILE):
        with open(BLOCK_FILE, 'r') as f:
            blocked_ids = json.load(f)
        if str(user.id) in blocked_ids:
            return

    for admin_id in ADMIN_IDS:
        try:
            context.bot.send_message(
                chat_id=admin_id,
                text=f"📩 پیام جدید از {user.full_name} (@{user.username}):\n\n{text}",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("✉️ پاسخ", callback_data=f"reply:{user.id}"),
                        InlineKeyboardButton("🚫 بلاک", callback_data=f"block:{user.id}"),
                        InlineKeyboardButton("✅ آنبلاک", callback_data=f"unblock:{user.id}")
                    ]
                ])
            )
        except:
            continue

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ پیامت با موفقیت فرستاده شد! دکتر گشاد حتماً می‌خونه 😄"
    )
    context.user_data["waiting_for_message"] = False

def handle_reply_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data
    if data.startswith("reply:"):
        user_id = data.split(":")[1]
        os.makedirs("data", exist_ok=True)
        with open(REPLY_STATE_FILE, 'w') as f:
            json.dump({"reply_to": user_id}, f)
        context.bot.send_message(chat_id=query.message.chat_id, text="✍️ حالا جوابتو بنویس...")

def handle_admin_reply(update: Update, context: CallbackContext):
    if not os.path.exists(REPLY_STATE_FILE):
        return
    with open(REPLY_STATE_FILE, 'r') as f:
        data = json.load(f)
    user_id = data.get("reply_to")
    if user_id:
        try:
            context.bot.send_message(chat_id=int(user_id), text=update.message.text)
            context.bot.send_message(chat_id=update.message.chat_id, text="✅ پاسخ فرستاده شد.")
        except:
            context.bot.send_message(chat_id=update.message.chat_id, text="❌ ارسال پیام ناموفق بود.")
    os.remove(REPLY_STATE_FILE)

def handle_block_unblock(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data
    user_id = data.split(":")[1]
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(BLOCK_FILE):
        with open(BLOCK_FILE, 'w') as f:
            json.dump([], f)

    with open(BLOCK_FILE, 'r') as f:
        blocked = json.load(f)

    if data.startswith("block:"):
        if user_id not in blocked:
            blocked.append(user_id)
            query.edit_message_text("✅ کاربر بلاک شد.")
    elif data.startswith("unblock:"):
        if user_id in blocked:
            blocked.remove(user_id)
            query.edit_message_text("✅ کاربر آزاد شد.")

    with open(BLOCK_FILE, 'w') as f:
        json.dump(blocked, f)
