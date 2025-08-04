from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, MessageHandler, Filters, CommandHandler, CallbackQueryHandler
import json
import os
from datetime import datetime

USERS_FILE = 'data/users.json'
BLOCKED_FILE = 'data/blocked.json'

# لیست ادمین‌ها از ENV
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(',')))

# شروع و خوش‌آمد
def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    # اگر بلاک شده باشد، اجازه نده
    if is_blocked(user_id):
        return

    # ذخیره کاربر جدید
    save_user(update)

    keyboard = [[InlineKeyboardButton("✉️ ارسال پیام", callback_data="send_message")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("سلام به ربات رسمی دکتر گشاد خوش اومدی.\nپیامتو ارسال کن به گشادیم برسم زودی جوابتو میدم 😎", reply_markup=reply_markup)

# ذخیره کاربر در فایل users.json
def save_user(update: Update):
    user = update.effective_user
    try:
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
    except:
        users = {}

    if str(user.id) not in users:
        users[str(user.id)] = {
            'name': user.full_name,
            'username': user.username or '',
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)

# بررسی بلاک بودن
def is_blocked(user_id):
    try:
        with open(BLOCKED_FILE, 'r') as f:
            blocked = json.load(f)
        return str(user_id) in blocked
    except:
        return False

# هندل کلیک دکمه ارسال پیام
def handle_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id

    if is_blocked(user_id):
        query.answer("شما بلاک شدید.")
        return

    query.answer()
    context.user_data['awaiting_message'] = True
    keyboard = []  # دکمه‌ای نمی‌سازیم در این مرحله
    query.message.reply_text("📝 پیامتو بنویس و بفرست:", reply_markup=InlineKeyboardMarkup(keyboard))

# دریافت پیام کاربر
def user_message(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = user.id

    if is_blocked(user_id):
        return

    # فقط درصورتی دریافت شود که منتظر پیام باشیم
    if not context.user_data.get('awaiting_message'):
        return

    # حذف انتظار بعد از دریافت پیام
    context.user_data['awaiting_message'] = False

    # ذخیره کاربر
    save_user(update)

    # ارسال به ادمین‌ها
    for admin_id in ADMIN_IDS:
        try:
            keyboard = [
                [
                    InlineKeyboardButton("✉️ پاسخ", callback_data=f"reply_{user_id}"),
                    InlineKeyboardButton("🚫 بلاک", callback_data=f"block_{user_id}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            if update.message.text:
                context.bot.send_message(chat_id=admin_id, text=f"📩 پیام از {user.full_name} (@{user.username or 'ندارد'})\n\n{update.message.text}", reply_markup=reply_markup)
            elif update.message.photo:
                photo = update.message.photo[-1].file_id
                context.bot.send_photo(chat_id=admin_id, photo=photo, caption=f"📩 عکس از {user.full_name} (@{user.username or 'ندارد'})", reply_markup=reply_markup)
            elif update.message.document:
                doc = update.message.document.file_id
                context.bot.send_document(chat_id=admin_id, document=doc, caption=f"📩 فایل از {user.full_name} (@{user.username or 'ندارد'})", reply_markup=reply_markup)
            elif update.message.voice:
                voice = update.message.voice.file_id
                context.bot.send_voice(chat_id=admin_id, voice=voice, caption=f"📩 ویس از {user.full_name} (@{user.username or 'ندارد'})", reply_markup=reply_markup)
        except:
            continue

    # پیام تأیید به کاربر
    keyboard = [[InlineKeyboardButton("🔁 ارسال مجدد", callback_data="send_message")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("✅ دکتر گشاد پیامتو دید. منتظر جواب بمون.", reply_markup=reply_markup)

# ثبت بلاک / آنبلاک
def handle_reply_buttons(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    admin_id = query.from_user.id

    if admin_id not in ADMIN_IDS:
        return

    if data.startswith("reply_"):
        user_id = int(data.split("_")[1])
        context.user_data['reply_to'] = user_id
        query.message.reply_text("✍️ پیام پاسخ‌ات رو بنویس:")
        query.answer("در حالت پاسخ‌دهی قرار گرفتید.")

    elif data.startswith("block_") or data.startswith("unblock_"):
        user_id = int(data.split("_")[1])
        try:
            with open(BLOCKED_FILE, 'r') as f:
                blocked = json.load(f)
        except:
            blocked = {}

        if data.startswith("block_"):
            blocked[str(user_id)] = True
            query.edit_message_reply_markup(
                InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ آنبلاک", callback_data=f"unblock_{user_id}")]
                ])
            )
            query.answer("کاربر بلاک شد.")
        else:
            if str(user_id) in blocked:
                blocked.pop(str(user_id))
            query.edit_message_reply_markup(
                InlineKeyboardMarkup([
                    [InlineKeyboardButton("🚫 بلاک", callback_data=f"block_{user_id}")]
                ])
            )
            query.answer("کاربر آنبلاک شد.")

        with open(BLOCKED_FILE, 'w') as f:
            json.dump(blocked, f)

# ارسال پاسخ از ادمین به کاربر
def admin_response(update: Update, context: CallbackContext):
    admin_id = update.effective_user.id
    if admin_id not in ADMIN_IDS:
        return

    user_id = context.user_data.get('reply_to')
    if not user_id:
        return

    try:
        if update.message.text:
            context.bot.send_message(chat_id=user_id, text=f"📬 پاسخ از دکتر گشاد:\n\n{update.message.text}")
        elif update.message.photo:
            photo = update.message.photo[-1].file_id
            context.bot.send_photo(chat_id=user_id, photo=photo, caption="📬 پاسخ از دکتر گشاد:")
        elif update.message.document:
            doc = update.message.document.file_id
            context.bot.send_document(chat_id=user_id, document=doc, caption="📬 پاسخ از دکتر گشاد:")
        elif update.message.voice:
            voice = update.message.voice.file_id
            context.bot.send_voice(chat_id=user_id, voice=voice, caption="📬 پاسخ از دکتر گشاد:")
    except:
        update.message.reply_text("❌ ارسال به کاربر ناموفق بود.")

    context.user_data.pop('reply_to', None)
