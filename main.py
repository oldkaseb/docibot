import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler
from datetime import datetime
import json

# متغیرها
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))
USERS_FILE = "users.json"
REPLY_STATE_FILE = "reply_state.json"

# ذخیره کاربران جدید
def save_user(user):
    try:
        if not os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'w') as f:
                json.dump({}, f)
        with open(USERS_FILE, 'r') as f:
            data = json.load(f)
        uid = str(user.id)
        if uid not in data:
            data[uid] = {
                "name": f"{user.first_name}",
                "username": f"@{user.username}" if user.username else "ندارد",
                "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            with open(USERS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
    except Exception as e:
        print("Error saving user:", e)

# دکمه پاسخ و بلاک

def get_admin_buttons(user_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✉️ پاسخ", callback_data=f"reply:{user_id}"),
            InlineKeyboardButton("🔒 بلاک", callback_data=f"block:{user_id}")
        ]
    ])

# شروع ربات
def start_handler(update: Update, context: CallbackContext):
    user = update.effective_user
    save_user(user)
    if str(user.id) in get_blocked_users():
        return
    keyboard = [[InlineKeyboardButton("✉️ ارسال پیام به دکتر گشاد", callback_data="send")]]
    update.message.reply_text(
        "سلام 👋\nبه ربات رسمی دکتر گشاد خوش اومدی.\nپیامتو ارسال کن، به گشادی برسون، زودی جوابتو میدیم!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# نمایش راهنما برای ادمین
def help_handler(update: Update, context: CallbackContext):
    if update.effective_user.id in ADMIN_IDS:
        update.message.reply_text("\ud83d\udd4a\ufe0f راهنما:\n/start - شروع ربات\n/help - همین پیام\n/stats - آمار کاربران\n/add_admin ID - افزودن ادمین\n/remove_admin ID - حذف ادمین\n/forall پیام - ارسال پیام همگانی")

# آمار کاربران
def stats_handler(update: Update, context: CallbackContext):
    if update.effective_user.id in ADMIN_IDS:
        with open(USERS_FILE, 'r') as f:
            data = json.load(f)
        text = "\u2705 کاربران ثبت‌شده: \n"
        for uid, info in data.items():
            text += f"\nID: {uid}\nنام: {info['name']}\nیوزرنیم: {info['username']}\nزمان استارت: {info['start_time']}\n"
        update.message.reply_text(text)

# پیام همگانی
def broadcast_handler(update: Update, context: CallbackContext):
    if update.effective_user.id in ADMIN_IDS:
        msg = update.message.text.replace("/forall", "").strip()
        if not msg:
            update.message.reply_text("متن پیام رو بعد از /forall بنویس.")
            return
        with open(USERS_FILE, 'r') as f:
            data = json.load(f)
        count = 0
        for uid in data:
            try:
                context.bot.send_message(chat_id=int(uid), text=msg)
                count += 1
            except:
                pass
        update.message.reply_text(f"\u2709️ پیام به {count} نفر ارسال شد.")

# افزودن ادمین
def add_admin(update: Update, context: CallbackContext):
    if update.effective_user.id in ADMIN_IDS:
        if len(context.args) != 1:
            update.message.reply_text("فرمت درست: /add_admin ID")
            return
        new_id = int(context.args[0])
        if new_id not in ADMIN_IDS:
            ADMIN_IDS.append(new_id)
            update.message.reply_text(f"ادمین {new_id} افزوده شد.")

# حذف ادمین
def remove_admin(update: Update, context: CallbackContext):
    if update.effective_user.id in ADMIN_IDS:
        if len(context.args) != 1:
            update.message.reply_text("فرمت درست: /remove_admin ID")
            return
        remove_id = int(context.args[0])
        if remove_id in ADMIN_IDS:
            ADMIN_IDS.remove(remove_id)
            update.message.reply_text(f"ادمین {remove_id} حذف شد.")

# کاربران بلاک شده
def get_blocked_users():
    if os.path.exists("blocked.json"):
        with open("blocked.json") as f:
            return json.load(f)
    return []

def block_user(uid):
    users = get_blocked_users()
    if uid not in users:
        users.append(uid)
        with open("blocked.json", "w") as f:
            json.dump(users, f)

# پیام کاربر

def user_message(update: Update, context: CallbackContext):
    user = update.effective_user
    if user.id in get_blocked_users():
        return
    save_user(user)
    for admin_id in ADMIN_IDS:
        context.bot.send_message(
            chat_id=admin_id,
            text=f"\ud83d\udce9 پیام از {user.full_name} (@{user.username or 'ندارد'})\nID: {user.id}\n\n{update.message.text}",
            reply_markup=get_admin_buttons(user.id)
        )
    context.bot.send_message(chat_id=update.effective_chat.id, text="✉️ پیامت ارسال شد برای دکتر گشاد!")

# هندلر کلیک دکمه‌ها
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user = query.from_user
    if user.id not in ADMIN_IDS:
        return

    data = query.data
    if data.startswith("reply:"):
        uid = data.split(":")[1]
        with open(REPLY_STATE_FILE, "w") as f:
            json.dump({"admin": user.id, "target": uid}, f)
        query.message.reply_text("✉️ پاسخ خود را ارسال کن:")

    elif data.startswith("block:"):
        uid = int(data.split(":")[1])
        block_user(uid)
        query.message.reply_text("❌ کاربر بلاک شد.")

    elif data == "send":
        context.bot.send_message(chat_id=query.message.chat_id, text="✍ حالا پیامتو تایپ کن و بفرست تا دکتر گشاد ببینه...")

# پاسخ ادمین به کاربر
def reply_message_handler(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if not os.path.exists(REPLY_STATE_FILE):
        return
    with open(REPLY_STATE_FILE) as f:
        data = json.load(f)
    if data.get("admin") != update.effective_user.id:
        return

    target_id = int(data.get("target"))
    try:
        context.bot.send_message(chat_id=target_id, text=f"📬 دکتر گشاد پاسخ داد:\n{update.message.text}")
        update.message.reply_text("✉️ پاسخ ارسال شد.")
    except:
        update.message.reply_text("❌ ارسال نشد. شاید کاربر بلاک کرده یا دیلیت کرده.")
    os.remove(REPLY_STATE_FILE)

# اجرای ربات
def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_handler))
    dp.add_handler(CommandHandler("help", help_handler))
    dp.add_handler(CommandHandler("stats", stats_handler))
    dp.add_handler(CommandHandler("forall", broadcast_handler))
    dp.add_handler(CommandHandler("add_admin", add_admin))
    dp.add_handler(CommandHandler("remove_admin", remove_admin))
    dp.add_handler(MessageHandler(Filters.text & Filters.private, reply_message_handler))
    dp.add_handler(MessageHandler(Filters.text & Filters.private, user_message))
    dp.add_handler(CallbackQueryHandler(button_handler))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
