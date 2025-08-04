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

    # فوروارد به همه ادمین‌ها + دکمه پاسخ/بلاک
    for admin_id in ADMIN_IDS:
        btns = [
            [
                InlineKeyboardButton("✉️ پاسخ", callback_data=f"reply_{chat_id}"),
                InlineKeyboardButton("🔒 بلاک", callback_data=f"block_{chat_id}")
            ]
        ]
        context.bot.send_message(
            chat_id=admin_id,
            text=f"📨 پیام از: {user.full_name} (@{user.username})\n🆔 {user.id}",
            reply_markup=InlineKeyboardMarkup(btns)
        )
        update.message.forward(chat_id=admin_id)

    # اطلاع به کاربر و ارائه دکمه جدید
    update.message.reply_text(
        "✅ دکتر گشاد پیامتو دید 😎",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✉️ ارسال پیام دیگر", callback_data="send_msg")]
        ])
    )
