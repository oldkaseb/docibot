from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from config import ADMIN_IDS
from utils.db import save_message, is_blocked, set_reply_state, get_reply_state, clear_reply_state, block_user, unblock_user

def user_message(update: Update, context: CallbackContext):
    user = update.effective_user
    chat_id = user.id
    if is_blocked(chat_id):
        return update.message.reply_text("شما توسط ادمین بلاک شده‌اید 🚫")
    save_message(user)
    for admin_id in ADMIN_IDS:
        btns = [[InlineKeyboardButton("✉️ پاسخ", callback_data=f"reply_{chat_id}"),
                 InlineKeyboardButton("🔒 بلاک", callback_data=f"block_{chat_id}")]]
        context.bot.send_message(chat_id=admin_id,
                                 text=f"📨 پیام از: {user.full_name} (@{user.username})\n🆔 {user.id}",
                                 reply_markup=InlineKeyboardMarkup(btns))
        update.message.forward(chat_id=admin_id)

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data
    admin_id = query.from_user.id
    if data.startswith("reply_"):
        user_id = int(data.split("_")[1])
        set_reply_state(admin_id, user_id)
        query.edit_message_reply_markup(reply_markup=None)
        context.bot.send_message(chat_id=admin_id, text="✉️ پیام خود را بنویس تا برای کاربر ارسال شود.")
    elif data.startswith("block_"):
        user_id = int(data.split("_")[1])
        block_user(user_id)
        query.edit_message_reply_markup(InlineKeyboardMarkup([[InlineKeyboardButton("🔓 آنبلاک", callback_data=f"unblock_{user_id}")]]))
        context.bot.send_message(admin_id, text="✅ کاربر بلاک شد.")
    elif data.startswith("unblock_"):
        user_id = int(data.split("_")[1])
        unblock_user(user_id)
        query.edit_message_reply_markup(InlineKeyboardMarkup([[InlineKeyboardButton("🔒 بلاک", callback_data=f"block_{user_id}")]]))
        context.bot.send_message(admin_id, text="✅ کاربر آنبلاک شد.")

def handle_admin_reply(update: Update, context: CallbackContext):
    admin_id = update.effective_user.id
    state = get_reply_state(admin_id)
    if state:
        context.bot.copy_message(chat_id=state, from_chat_id=admin_id, message_id=update.message.message_id)
        clear_reply_state(admin_id)
        update.message.reply_text("✅ پیام برای کاربر ارسال شد.")

user_message_handler = MessageHandler(Filters.private & Filters.text & ~Filters.command, user_message)
reply_message_handler = MessageHandler(Filters.private & Filters.all & ~Filters.command, handle_admin_reply)
button_callback_handler = CallbackQueryHandler(button_handler)