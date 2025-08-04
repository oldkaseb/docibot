from telegram import Update
from telegram.ext import CallbackContext
from utils.helpers import broadcast
import os

def forall_command(update: Update, context: CallbackContext):
    if not update.message.reply_to_message:
        update.message.reply_text("❗ این دستور باید روی یک پیام ریپلای بشه.")
        return

    admin_ids = list(map(int, os.getenv("ADMIN_IDS", "").split(',')))
    if update.effective_user.id not in admin_ids:
        update.message.reply_text("⛔ فقط ادمین‌ها اجازه ارسال پیام همگانی دارن.")
        return

    success, fail = broadcast(context.bot, update.message.reply_to_message)
    update.message.reply_text(f"✅ پیام برای {success} نفر ارسال شد.\n❌ ناموفق: {fail}")
