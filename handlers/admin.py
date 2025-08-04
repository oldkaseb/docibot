from telegram import Update
from telegram.ext import CallbackContext
from utils.db import (
    get_all_users,
    get_admin_ids,
    add_admin_id,
    remove_admin_id,
    block_user,
    unblock_user
)

def stats_command(update: Update, context: CallbackContext):
    admin_ids = get_admin_ids()
    if update.effective_user.id not in admin_ids:
        return

    users = get_all_users()
    total = len(users)
    msg = "📊 آمار کاربران:\n\n"
    for user_id, data in users.items():
        msg += f"🆔 {user_id} | 👤 {data.get('name', 'نامشخص')} | ⏰ {data.get('joined', '---')}\n"
    msg += f"\n✅ مجموع: {total} نفر"
    update.message.reply_text(msg)

def help_command(update: Update, context: CallbackContext):
    admin_ids = get_admin_ids()
    if update.effective_user.id not in admin_ids:
        return

    update.message.reply_text(
        "🛠 دستورات ادمین:\n"
        "/stats - مشاهده آمار کاربران\n"
        "/addadmin [id] - افزودن ادمین\n"
        "/removeadmin [id] - حذف ادمین\n"
        "/forall - پیام همگانی (روی پیام ریپلای کن)\n"
        "/help - همین راهنما"
    )

def forall_command(update: Update, context: CallbackContext):
    admin_ids = get_admin_ids()
    if update.effective_user.id not in admin_ids:
        return

    if not update.message.reply_to_message:
        update.message.reply_text("❗ روی یک پیام ریپلای کن تا برای همه ارسال شود.")
        return

    users = get_all_users()
    success = 0
    for user_id in users:
        try:
            context.bot.copy_message(
                chat_id=int(user_id),
                from_chat_id=update.message.chat.id,
                message_id=update.message.reply_to_message.message_id
            )
            success += 1
        except:
            continue

    update.message.reply_text(f"✅ پیام برای {success} کاربر ارسال شد.")

def add_admin(update: Update, context: CallbackContext):
    admin_ids = get_admin_ids()
    if update.effective_user.id not in admin_ids:
        return

    if not context.args:
        update.message.reply_text("❗ آیدی عددی کاربر را وارد کن.")
        return

    try:
        user_id = int(context.args[0])
        add_admin_id(user_id)
        update.message.reply_text(f"✅ کاربر {user_id} به لیست ادمین‌ها افزوده شد.")
    except:
        update.message.reply_text("⛔ خطا در افزودن ادمین.")

def remove_admin(update: Update, context: CallbackContext):
    admin_ids = get_admin_ids()
    if update.effective_user.id not in admin_ids:
        return

    if not context.args:
        update.message.reply_text("❗ آیدی عددی کاربر را وارد کن.")
        return

    try:
        user_id = int(context.args[0])
        remove_admin_id(user_id)
        update.message.reply_text(f"✅ کاربر {user_id} از لیست ادمین‌ها حذف شد.")
    except:
        update.message.reply_text("⛔ خطا در حذف ادمین.")
