from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, MessageHandler, CallbackQueryHandler, Filters

def user_message(update: Update, context: CallbackContext):
    user = update.effective_user
    chat_id = user.id

    # بررسی بلاک بودن
    if is_blocked(chat_id):
        return update.message.reply_text("شما توسط ادمین بلاک شده‌اید 🚫")

    # ذخیره کاربر در دیتابیس
    save_message(user)

    # ارسال پیام به همه ادمین‌ها
    for admin_id in ADMIN_IDS:
        # دکمه‌های پاسخ و بلاک
        buttons = [
            [
                InlineKeyboardButton("✉️ پاسخ", callback_data=f"reply_{chat_id}"),
                InlineKeyboardButton("🔒 بلاک", callback_data=f"block_{chat_id}")
            ]
        ]

        # ارسال توضیح کاربر
        context.bot.send_message(
            chat_id=admin_id,
            text=f"📨 پیام از: {user.full_name} (@{user.username})\nID: <code>{user.id}</code>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

        # کپی پیام اصلی (با مدیا یا متن)
        try:
            update.message.copy(chat_id=admin_id)
        except Exception as e:
            context.bot.send_message(admin_id, text=f"⚠️ خطا در ارسال پیام کاربر:\n{e}")

    # اعلام به کاربر که پیامش ارسال شد
    update.message.reply_text(
        "✅ پیام شما ارسال شد و دکتر گشاد اون رو دید 😎",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✉️ ارسال پیام دیگر", callback_data="send_msg")]
        ])
    )
