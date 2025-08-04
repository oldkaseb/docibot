import os
import json
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))
BLOCKED_USERS_FILE = "blocked_users.json"
ADMINS_FILE = "admins.json"

# بارگذاری ادمین‌ها از فایل
if os.path.exists(ADMINS_FILE):
    with open(ADMINS_FILE, "r") as f:
        admins = json.load(f)
else:
    admins = ADMIN_IDS.copy()

# لیست بلاک شده‌ها
if os.path.exists(BLOCKED_USERS_FILE):
    with open(BLOCKED_USERS_FILE, "r") as f:
        blocked_users = json.load(f)
else:
    blocked_users = []

# ذخیره دیتا

def save_data():
    with open(BLOCKED_USERS_FILE, "w") as f:
        json.dump(blocked_users, f)
    with open(ADMINS_FILE, "w") as f:
        json.dump(admins, f)

# استارت

def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id in blocked_users:
        return
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✉️ ارسال پیام به دکتر گشاد", callback_data="send_message")]
    ])
    update.message.reply_text("👋 سلام\nبه ربات رسمی دکتر گشاد خوش اومدی.\nپیامتو ارسال کن، به گشادم برسون، زودی جوابتو میدیم!", reply_markup=keyboard)

# راهنما

def help_command(update: Update, context: CallbackContext):
    text = """
📌 راهنما:
/start - شروع ربات
/help - همین پیام
/stats - آمار
/forall - پیام همگانی
/add_admin <id>
/remove_admin <id>
"""
    update.message.reply_text(text)

# ارسال پیام کاربر
user_reply_waiting = {}

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    if query.data == "send_message":
        user_reply_waiting[user_id] = True
        context.bot.send_message(chat_id=user_id, text="✍️ حالا پیام تو بنویس و بفرست تا برای دکتر گشاد ارسال بشه...")
    query.answer()

# دریافت پیام کاربر

def user_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id in blocked_users:
        return
    if not user_reply_waiting.get(user_id):
        return
    user_reply_waiting.pop(user_id)
    message_text = update.message.text
    for admin_id in admins:
        try:
            context.bot.send_message(
                chat_id=admin_id,
                text=f"📩 پیام از {update.effective_user.mention_html()}\nID: <code>{user_id}</code>\n\n{message_text}",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("✉️ پاسخ", callback_data=f"reply_{user_id}"),
                        InlineKeyboardButton("🔒 بلاک", callback_data=f"block_{user_id}")
                    ]
                ]),
                parse_mode='HTML'
            )
        except:
            continue
    update.message.reply_text("✅ ارسال شد!")

# مدیریت کلیک‌های ادمین
reply_targets = {}

def admin_buttons(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data
    admin_id = query.from_user.id
    if admin_id not in admins:
        return

    if data.startswith("reply_"):
        user_id = int(data.split("_")[1])
        reply_targets[admin_id] = user_id
        context.bot.send_message(chat_id=admin_id, text="✍️ پیام خود را بنویسید تا برای کاربر ارسال شود:")

    elif data.startswith("block_"):
        user_id = int(data.split("_")[1])
        if user_id not in blocked_users:
            blocked_users.append(user_id)
            save_data()
            context.bot.send_message(chat_id=admin_id, text=f"Blocked {user_id}", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔓 آنبلاک", callback_data=f"unblock_{user_id}")]
            ]))

    elif data.startswith("unblock_"):
        user_id = int(data.split("_")[1])
        if user_id in blocked_users:
            blocked_users.remove(user_id)
            save_data()
            context.bot.send_message(chat_id=admin_id, text=f"Unblocked {user_id}")

# دریافت پیام ادمین

def admin_reply(update: Update, context: CallbackContext):
    admin_id = update.effective_user.id
    if admin_id in reply_targets:
        user_id = reply_targets.pop(admin_id)
        context.bot.send_message(chat_id=user_id, text=f"📬 دکتر گشاد دید: {update.message.text}")
        update.message.reply_text("✅ ارسال شد!")

# آمار

def stats(update: Update, context: CallbackContext):
    if update.effective_user.id in admins:
        update.message.reply_text(f"آمار: {len(user_reply_waiting)}")

# پیام همگانی

def forall(update: Update, context: CallbackContext):
    if update.effective_user.id in admins:
        text = update.message.text.split(" ", 1)
        if len(text) < 2:
            return update.message.reply_text("متن پیام را وارد کن")
        message = text[1]
        for user_id in user_reply_waiting:
            try:
                context.bot.send_message(chat_id=user_id, text=message)
            except:
                continue
        update.message.reply_text("✅ ارسال شد")

# افزودن و حذف ادمین

def add_admin(update: Update, context: CallbackContext):
    if update.effective_user.id in admins:
        parts = update.message.text.split()
        if len(parts) == 2:
            new_id = int(parts[1])
            if new_id not in admins:
                admins.append(new_id)
                save_data()
                update.message.reply_text(f"✅ ادمین اضافه شد: {new_id}")

def remove_admin(update: Update, context: CallbackContext):
    if update.effective_user.id in admins:
        parts = update.message.text.split()
        if len(parts) == 2:
            target_id = int(parts[1])
            if target_id in admins:
                admins.remove(target_id)
                save_data()
                update.message.reply_text(f"❌ ادمین حذف شد: {target_id}")

# ران
updater = Updater(BOT_TOKEN)
dp = updater.dispatcher

# هندلرها
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("help", help_command))
dp.add_handler(CommandHandler("stats", stats))
dp.add_handler(CommandHandler("forall", forall))
dp.add_handler(CommandHandler("add_admin", add_admin))
dp.add_handler(CommandHandler("remove_admin", remove_admin))
dp.add_handler(MessageHandler(Filters.text & Filters.user(user_id=admins), admin_reply))
dp.add_handler(MessageHandler(Filters.text & (~Filters.command), user_message))
dp.add_handler(CallbackQueryHandler(button_handler, pattern="^send_message$"))
dp.add_handler(CallbackQueryHandler(admin_buttons))

updater.start_polling()
updater.idle()
