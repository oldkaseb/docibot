from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext
from config import ADMIN_IDS
from utils.helpers import broadcast

pending_broadcast = {}

def forall_command(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return
    pending_broadcast[update.effective_user.id] = True
    update.message.reply_text("خب حالا گشاد بازی بسه 😒\nفور آل بزن ببینم چی میگی ✉️")

def handle_broadcast_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id in pending_broadcast:
        del pending_broadcast[user_id]
        sent, failed = broadcast(context.bot, update.message)
        update.message.reply_text(f"✅ پیام همگانی ارسال شد.\n🎯 موفق: {sent} | ❌ ناموفق: {failed}")

forall_init_handler = CommandHandler("forall", forall_command)