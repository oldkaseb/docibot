import os
import json
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler
from datetime import datetime

# --- ENV VARIABLES ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))
USERS_FILE = "users.json"
WAITING_MESSAGE = {}
BLOCKED_USERS = []

# --- HELPERS ---
def save_user(user):
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
    uid = str(user.id)
    if uid not in users:
        users[uid] = {
            "name": user.full_name,
            "username": user.username or "-",
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=2)

def get_admin_keyboard(user_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✉️ پاسخ", callback_data=f"reply:{user_id}"),
            InlineKeyboardButton("🔒 بلاک", callback_data=f"block:{user_id}")
        ]
    ])

# --- HANDLERS ---
def start(update: Update, context: CallbackContext):
    save_user(update.effective_user)
    keyboard = [[InlineKeyboardButton("✉️ ارسال پیام به دکتر گشاد", callback_data="start_msg")]]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="👋\nبه ربات رسمی دکتر گشاد خوش اومدی.\nپیامتو ارسال کن ، به گشادیم برسون، زودی جوابتو میدیم!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def help_command(update: Update, context: CallbackContext):
    if update.effective_user.id in ADMIN_IDS:
        update.message.reply_text("\ud83d\udd4c\n/start - \u0634\u0631\u0648\u0639 \u0631\u0628\u0627\u062a\n/help - \u0647\u0645\u06cc\u0646 \u067e\u06cc\u0627\u0645\n/stats - \u0622\u0645\0627\0631\n/forall - \u067e\u06cc\0627\0645 \u0647\0645\06af\0627\0646\06cc\n/add_admin <id>\n/remove_admin <id>")

def stats(update: Update, context: CallbackContext):
    if update.effective_user.id in ADMIN_IDS:
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
        text = f"\ud83d\udcca\nTotal users: {len(users)}"
        update.message.reply_text(text)

def forall(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return
    msg = " ".join(context.args)
    if not msg:
        update.message.reply_text("/forall <message>")
        return
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
    for uid in users:
        try:
            context.bot.send_message(chat_id=int(uid), text=msg)
        except:
            continue
    update.message.reply_text("Done sending.")

def add_admin(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return
    new_id = int(context.args[0])
    if new_id not in ADMIN_IDS:
        ADMIN_IDS.append(new_id)
        update.message.reply_text(f"Added admin: {new_id}")

def remove_admin(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return
    rem_id = int(context.args[0])
    if rem_id in ADMIN_IDS:
        ADMIN_IDS.remove(rem_id)
        update.message.reply_text(f"Removed admin: {rem_id}")

def callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = update.effective_user.id
    query.answer()

    if query.data == "start_msg":
        WAITING_MESSAGE[user_id] = True
        context.bot.send_message(chat_id=user_id, text="✍️ حالا پیامتو بفرست ...")

    elif query.data.startswith("reply:"):
        target = int(query.data.split(":")[1])
        context.user_data['reply_to'] = target
        context.bot.send_message(chat_id=user_id, text="پیام تو بفرست تا براش بفرستم")

    elif query.data.startswith("block:"):
        bid = int(query.data.split(":")[1])
        BLOCKED_USERS.append(bid)
        context.bot.send_message(chat_id=user_id, text=f"Blocked {bid}")

def user_message(update: Update, context: CallbackContext):
    uid = update.effective_user.id
    if uid in BLOCKED_USERS:
        return

    # پاسخ به کاربر
    if context.user_data.get("reply_to"):
        target_id = context.user_data.pop("reply_to")
        context.bot.send_message(chat_id=target_id, text=f"📩 پیام از دکتر گشاد:")
        context.bot.send_message(chat_id=target_id, text=update.message.text)
        update.message.reply_text("ارسال شد!")
        return

    # پیام جدید از کاربر
    if WAITING_MESSAGE.get(uid):
        WAITING_MESSAGE.pop(uid)
        for admin_id in ADMIN_IDS:
            context.bot.send_message(
                chat_id=admin_id,
                text=f"📨 پیام از {update.effective_user.full_name} (@{update.effective_user.username or '---'})\nID: {uid}",
                reply_markup=get_admin_keyboard(uid)
            )
            context.bot.send_message(chat_id=admin_id, text=update.message.text)
        update.message.reply_text("✅ پیامت ارسال شد برای دکتر گشاد!")

# --- MAIN ---
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("forall", forall))
    dp.add_handler(CommandHandler("add_admin", add_admin))
    dp.add_handler(CommandHandler("remove_admin", remove_admin))
    dp.add_handler(CallbackQueryHandler(callback_handler))
    dp.add_handler(MessageHandler(Filters.text & Filters.private, user_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
