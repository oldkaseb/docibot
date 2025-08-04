from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext
import json
from datetime import datetime
import os

USERS_FILE = 'data/users.json'
BLOCK_FILE = 'data/blocked.json'

# دستور /start
def start_command(update: Update, context: CallbackContext):
    user = update.effective_user

    # ذخیره اطلاعات در فایل users.json
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

    # دکمه ارسال پیام
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📨 فرستادن پیام به دکتر گشاد", callback_data="start_message")]
    ])

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="سلام! 👋\nمی‌تونی یه پیام واسه دکتر گشاد بفرستی. روی دکمه زیر بزن و تایپ کن 😎👇",
        reply_markup=keyboard
    )


# واکنش به دکمه ارسال پیام
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


# دریافت پیام کاربر
def user_message(update: Update, context: CallbackContext):
    user = update.effective_user
    text = update.message.text

    # اگر کاربر در حالت پیام‌دهی نیست، کاری نکن
    if not context.user_data.get("waiting_for_message"):
        return

    # بررسی بلاک
    if os.path.exists(BLOCK_FILE):
        with open(BLOCK_FILE, 'r') as f:
            blocked_ids = json.load(f)
        if user.id in blocked_ids:
            return

    # ارسال پیام به همه ادمین‌ها
    admin_ids = list(map(int, os.getenv("ADMIN_IDS", "").split(',')))
    for admin_id in admin_ids:
        try:
            context.bot.send_message(
                chat_id=admin_id,
                text=f"📩 پیام جدید از {user.full_name} (@{user.username}):\n\n{text}",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("✉️ پاسخ", callback_data=f"reply:{user.id}"),
                        InlineKeyboardButton("🚫 بلاک", callback_data=f"block:{user.id}")
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
