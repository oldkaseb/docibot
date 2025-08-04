from utils.db import get_all_users, add_user as save_user
from telegram import Bot

def send_to_admins(bot: Bot, admin_ids, text):
    for admin_id in admin_ids:
        try:
            bot.send_message(chat_id=admin_id, text=text)
        except:
            pass

def broadcast(bot: Bot, message):
    users = get_all_users()
    success = 0
    fail = 0
    for uid in users:
        try:
            bot.copy_message(chat_id=int(uid), from_chat_id=message.chat.id, message_id=message.message_id)
            success += 1
        except:
            fail += 1
    return success, fail

def save_new_user(user_id, user_data):
    save_user(user_id, user_data)
