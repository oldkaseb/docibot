import json
import os

DB_FILE = "data/users.json"

# دریافت لیست کامل کاربران
def get_all_users():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

# دریافت کاربران بلاک‌شده
def get_blocked_users():
    users = get_all_users()
    blocked = {}
    for uid, info in users.items():
        if info.get("blocked", False):
            blocked[uid] = info
    return blocked

# افزودن کاربر جدید به لیست
def save_user(user_id, full_name, username):
    users = get_all_users()
    if str(user_id) not in users:
        users[str(user_id)] = {
            "name": full_name,
            "username": username,
            "blocked": False
        }
        with open(DB_FILE, "w") as f:
            json.dump(users, f, indent=2)

# بلاک کردن کاربر
def block_user(user_id):
    users = get_all_users()
    if str(user_id) in users:
        users[str(user_id)]["blocked"] = True
        with open(DB_FILE, "w") as f:
            json.dump(users, f, indent=2)

# آنبلاک کردن کاربر
def unblock_user(user_id):
    users = get_all_users()
    if str(user_id) in users:
        users[str(user_id)]["blocked"] = False
        with open(DB_FILE, "w") as f:
            json.dump(users, f, indent=2)

# دریافت لیست آیدی ادمین‌ها
def get_admins():
    admins_file = "data/admins.json"
    if not os.path.exists(admins_file):
        return []
    with open(admins_file, "r") as f:
        return json.load(f)

# افزودن ادمین جدید
def add_admin(user_id):
    admins = get_admins()
    if user_id not in admins:
        admins.append(user_id)
        with open("data/admins.json", "w") as f:
            json.dump(admins, f)

# حذف ادمین
def remove_admin(user_id):
    admins = get_admins()
    if user_id in admins:
        admins.remove(user_id)
        with open("data/admins.json", "w") as f:
            json.dump(admins, f)
