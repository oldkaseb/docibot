from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    CallbackContext,
)

from utils.db import save_message, is_blocked
from config import ADMIN_IDS


def user_message(update: Update, context: CallbackContext):
    user = update.effective_user
    chat_id = user.id

    if is_blocked(chat_id):
        return update.message.reply_text("شما توسط ادمین بلاک شده‌اید 🚫")

    # ذخیره پیام در دیتابیس (json)
    save_message(user)

    # دکمه‌ها برای ادمین (پاسخ و بلاک)
    buttons = [
        [
            InlineKeyboardButton("✉️ پاسخ", callback_data=f"reply_{chat_id}"),
            InlineKeyboardButton("🔒 بلاک", callback_data=f"block_{chat_id}")
        ]
    ]

    # ارسال پیام به ادمین‌ها
    for admin_id in ADMIN_IDS:
        try:
            # مشخصات کاربر
            context.bot.send_message(
                chat_id=admin_id,
                text=f"📨 پیام از: {user.full_name} (@{user.username})\nID: <code>{chat_id}</code>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            # کپی پیام اصلی کاربر
            update.message.copy(chat_id=admin_id)
        except Exception as e:
            context.bot.send_message(admin_id, text=f"⚠️ خطا در ارسال پیام:\n{e}")

    # اطلاع‌رسانی به کاربر
    update.message.reply_text(
        "✅ پیام شما ارسال شد و دکتر گشاد اون رو دید 😎",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✉️ ارسال پیام دیگر", callback_data="send_msg")]
        ])
    )
