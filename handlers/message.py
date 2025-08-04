from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext
import json
import os

BLOCK_FILE = 'data/blocked.json'

# دکمه شروع و ارسال پیام
def start_command(update: Update, context: CallbackContext):
    user = update.effective_user
    save_user(user)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("ارسال پیام به دکتر گشاد", callback_data="send_message")]
    ])
    update.message.reply_text("👋 خوش اومدی! اگه میخوای پیامی به تیم پشتیبانی بدی، رو دکمه زیر بزن.", reply_markup=keyboard)

# هندلر کلیک روی دکمه‌ها
def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id

    if query.data == "send_message":
        context.user_data["awaiting_message"] = True
        query.edit_message_text("📝 خیلی خب! منتظرم پیام‌تو بنویسی و بفرستی.")

    elif query.data.startswith("reply_"):
        target_id = int(query.data.split("_")[1])
        context.user_data['reply_to'] = target_id
        query.answer()
        query.message.reply_text("✏️ حالا متنتو بنویس تا براش بفرستم")

    elif query.data.startswith("block_"):
        target_id = int(query.data.split("_")[1])
        block_user(target_id)
        query.answer("کاربر بلاک شد ❌")
        query.edit_message_reply_markup(reply_markup=None)

    elif query.data.startswith("unblock_"):
        target_id = int(query.data.split("_")[1])
        unblock_user(target_id)
        query.answer("کاربر آنبلاک شد ✅")
        query.edit_message_reply_markup(reply_markup=None)

# دریافت پیام‌های کاربران و ارسال به ادمین
def user_message(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = user.id

    if is_blocked(user_id):
        return

    if context.user_data.get("awaiting_message"):
        text = update.message.text
        from handlers.config import ADMIN_IDS

        for admin_id in ADMIN_IDS:
            context.bot.send_message(
                chat_id=admin_id,
                text=f"📩 پیام جدید از {user.full_name} (@{user.username or 'نداره'}):\n\n{text}",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("✉️ پاسخ", callback_data=f"reply_{user_id}"),
                        InlineKeyboardButton("❌ بلاک", callback_data=f"block_{user_id}")
                    ]
                ])
            )
        context.user_data["awaiting_message"] = False
        update.message.reply_text("✅ پیامت رسید، دکتر گشاد دیدش 😄")
        return

    if context.user_data.get('reply_to'):
        target_id = context.user_data['reply_to']
        try:
            context.bot.send_message(chat_id=target_id, text=update.message.text)
            update.message.reply_text("✉️ پیام ارسال شد")
        except:
            update.message.reply_text("❌ ارسال نشد! شاید بلاکمون کرده 😕")
        context.user_data['reply_to'] = None

# ذخیره کاربر
def save_user(user):
    os.makedirs("data", exist_ok=True)
    with open("data/users.json", "r+") as f:
        data = json.load(f)
        if str(user.id) not in data:
            data[str(user.id)] = {
                "name": user.full_name,
                "username": user.username,
                "start_time": str(update_time_now())
            }
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()

# بلاک و آنبلاک

def is_blocked(user_id):
    if not os.path.exists(BLOCK_FILE):
        return False
    with open(BLOCK_FILE, 'r') as f:
        return user_id in json.load(f)

def block_user(user_id):
    with open(BLOCK_FILE, 'r+') as f:
        data = json.load(f)
        if user_id not in data:
            data.append(user_id)
            f.seek(0)
            json.dump(data, f)
            f.truncate()

def unblock_user(user_id):
    with open(BLOCK_FILE, 'r+') as f:
        data = json.load(f)
        if user_id in data:
            data.remove(user_id)
            f.seek(0)
            json.dump(data, f)
            f.truncate()

# زمان شروع کاربر

def update_time_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
