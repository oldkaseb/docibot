from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import os
import json
from datetime import datetime

ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(',')))
USERS_FILE = 'data/users.json'
BLOCK_FILE = 'data/blocked.json'
RESPOND_FILE = 'data/respond.json'

def add_admin(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if not context.args:
        update.message.reply_text("لطفاً آیدی عددی ادمین جدید را وارد کنید.")
        return
    new_admin = int(context.args[0])
    if new_admin in ADMIN_IDS:
        update.message.reply_text("این کاربر از قبل ادمین است.")
        return
    ADMIN_IDS.append(new_admin)
    update.message.reply_text("✅ ادمین جدید اضافه شد.")

def remove_admin(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if not context.args:
        update.message.reply_text("لطفاً آیدی عددی ادمین را برای حذف وارد کنید.")
        return
    admin_id = int(context.args[0])
    if admin_id in ADMIN_IDS:
        ADMIN_IDS.remove(admin_id)
        update.message.reply_text("✅ ادمین حذف شد.")
    else:
        update.message.reply_text("این کاربر ادمین نیست.")

def forall(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return
    update.message.reply_text("✉️ لطفاً پیام همگانی را ارسال کنید...")
    context.user_data["broadcast"] = True

def handle_broadcast_message(update: Update, context: CallbackContext):
    if not context.user_data.get("broadcast"):
        return
    context.user_data["broadcast"] = False
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    sent, failed = 0, 0
    for user_id in users:
        try:
            context.bot.send_message(chat_id=int(user_id), text=update.message.text)
            sent += 1
        except:
            failed += 1
    update.message.reply_text(f"📤 پیام به {sent} نفر ارسال شد. ❌ ناموفق: {failed}")

def stats(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    total = len(users)
    msg = f"📊 آمار کاربران:\n\nتعداد کل: {total}\n\n"
    for uid, info in users.items():
        name = info.get("name", "ندارد")
        time = info.get("time", "نامشخص")
        msg += f"🆔 {uid} | 👤 {name} | ⏰ {time}\n"
    update.message.reply_text(msg)

def help_command(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return
    update.message.reply_text(
        "📘 راهنمای ادمین:\n\n"
        "/admin <id> ➤ افزودن ادمین جدید\n"
        "/removeadmin <id> ➤ حذف ادمین\n"
        "/forall ➤ ارسال پیام همگانی\n"
        "/stats ➤ مشاهده آمار کاربران\n"
        "/help ➤ نمایش این راهنما"
    )

def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    query.answer()

    if data.startswith("reply_"):
        user_id = int(data.split("_")[1])
        context.user_data["reply_to"] = user_id
        query.edit_message_text("✏️ لطفاً پاسخ خود را ارسال کنید...")
        return

    if data.startswith("block_"):
        user_id = int(data.split("_")[1])
        with open(BLOCK_FILE, 'r+') as f:
            blocked = json.load(f)
            if user_id not in blocked:
                blocked.append(user_id)
                f.seek(0)
                json.dump(blocked, f)
                f.truncate()
        query.edit_message_text("⛔️ کاربر مسدود شد.")
        return

    if data.startswith("unblock_"):
        user_id = int(data.split("_")[1])
        with open(BLOCK_FILE, 'r+') as f:
            blocked = json.load(f)
            if user_id in blocked:
                blocked.remove(user_id)
                f.seek(0)
                json.dump(blocked, f)
                f.truncate()
        query.edit_message_text("✅ کاربر رفع بلاک شد.")
        return

def handle_admin_reply(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return
    reply_to = context.user_data.get("reply_to")
    if not reply_to:
        return
    context.bot.send_message(chat_id=reply_to, text="🧑‍⚕️ دکتر گشاد پیامتو دید و پاسخ داد:\n\n" + update.message.text)
    update.message.reply_text("✅ پاسخ شما ارسال شد.")
    context.user_data["reply_to"] = None

def forward_to_admin(update: Update, context: CallbackContext):
    user = update.effective_user
    sender_id = user.id
    sender_name = user.full_name
    message_text = update.message.text or "— بدون متن —"

    with open(BLOCK_FILE, 'r') as f:
        blocked = json.load(f)
    if sender_id in blocked:
        return

    # ذخیره کاربر
    with open(USERS_FILE, 'r+') as f:
        users = json.load(f)
        if str(sender_id) not in users:
            users[str(sender_id)] = {
                "name": sender_name,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            f.seek(0)
            json.dump(users, f)
            f.truncate()

    # ساخت دکمه
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✉️ پاسخ", callback_data=f"reply_{sender_id}"),
         InlineKeyboardButton("⛔️ بلاک", callback_data=f"block_{sender_id}")],
        [InlineKeyboardButton("✅ رفع بلاک", callback_data=f"unblock_{sender_id}")]
    ])

    # پیام چند خطی واضح برای ادمین
    text = f"""📩 پیام جدید از کاربر:

👤 نام: {sender_name}
🆔 آیدی: {sender_id}
📬 پیام: {message_text}"""

    for admin_id in ADMIN_IDS:
        try:
            context.bot.send_message(chat_id=admin_id, text=text, reply_markup=keyboard)
        except:
            continue

    update.message.reply_text("✅ پیام شما ارسال شد و در حال بررسی است.")

