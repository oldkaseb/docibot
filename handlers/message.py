from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
)
from telegram.ext import CallbackContext
import json
from datetime import datetime
import os

USERS_FILE = 'data/users.json'
BLOCK_FILE = 'data/blocked.json'
REPLY_STATE = {}

def start_command(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = str(user.id)

    with open(USERS_FILE, 'r+') as f:
        users = json.load(f)
        if user_id not in users:
            users[user_id] = {
                'name': user.full_name,
                'username': user.username,
                'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            f.seek(0)
            json.dump(users, f, indent=4)
            f.truncate()

    with open(BLOCK_FILE, 'r') as f:
        blocked = json.load(f)
        if int(user_id) in blocked:
            update.message.reply_text("شما توسط ادمین مسدود شده‌اید.")
            return

    keyboard = [[InlineKeyboardButton("✉️ ارسال پیام", callback_data='send_message')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("به ربات خوش آمدید!\nبرای ارسال پیام به ادمین، دکمه زیر را بزنید 👇", reply_markup=reply_markup)

def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id

    with open(BLOCK_FILE, 'r') as f:
        blocked = json.load(f)
        if user_id in blocked:
            query.answer("شما مسدود شده‌اید.")
            return

    if query.data == 'send_message':
        REPLY_STATE[user_id] = True
        context.bot.send_message(
            chat_id=user_id,
            text="پیام خود را ارسال کنید...",
            reply_markup=ReplyKeyboardRemove()
        )
        context.bot.delete_message(chat_id=user_id, message_id=query.message.message_id)

def user_message(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = user.id
    message = update.message

    with open(BLOCK_FILE, 'r') as f:
        blocked = json.load(f)
        if user_id in blocked:
            return

    if REPLY_STATE.get(user_id):
        del REPLY_STATE[user_id]

        with open(USERS_FILE, 'r') as f:
            users = json.load(f)

        user_info = users.get(str(user_id), {})
        name = user_info.get('name', user.full_name)
        username = user_info.get('username', user.username)
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # ساخت دکمه پاسخ و بلاک
        buttons = [
            [
                InlineKeyboardButton("✉️ پاسخ", callback_data=f"reply_{user_id}"),
                InlineKeyboardButton("⛔ بلاک", callback_data=f"block_{user_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)

        text = f"📥 پیام جدید:\n\n👤 {name} | @{username or 'ندارد'}\n🆔 {user_id}\n🕒 {time}"
        context.bot.send_message(chat_id=int(os.getenv("ADMIN_IDS").split(",")[0]), text=text, reply_markup=reply_markup)
        if message.text:
            context.bot.send_message(chat_id=int(os.getenv("ADMIN_IDS").split(",")[0]), text=message.text)

        context.bot.send_message(chat_id=user_id, text="✅ پیام شما ارسال شد. دکتر گشاد دریافت کرد!")

        # دکمه ارسال مجدد
        keyboard = [[InlineKeyboardButton("✉️ ارسال مجدد", callback_data='send_message')]]
        context.bot.send_message(chat_id=user_id, text="اگر می‌خواهید پیام جدیدی ارسال کنید:", reply_markup=InlineKeyboardMarkup(keyboard))
