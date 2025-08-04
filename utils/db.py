import json
import os

USERS_FILE = "data/users.json"
BLOCKED_FILE = "data/blocked.json"
ADMINS_FILE = "data/admins.json"

# ذخیره‌سازی دیتا در فایل
def save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f)

# بارگذاری دیتا از فایل
def load_json(filepath):
    if not os.path.exists(filepath):
        return {}
    with open(filepath, 'r') as f:
        return json.load(f)

# --- مدیریت کاربران ---
def save_user(user_id, name, username):
    users = load_json(USERS_FILE)
    if str(user_id) not in users:
        users[str(user_id)] = {
            "name": name,
            "username": username
        }
        save_json(USERS_FILE, users)

def get_all_users():
    return load_json(USERS_FILE)

# --- مدیریت بلاک ---
def add_blocked_user(user_id):
    blocked = load_json(BLOCKED_FILE)
    blocked[str(user_id)] = True
    save_json(BLOCKED_FILE, blocked)

def remove_blocked_user(user_id):
    blocked = load_json(BLOCKED_FILE)
    if str(user_id) in blocked:
        del blocked[str(user_id)]
        save_json(BLOCKED_FILE, blocked)

def is_user_blocked(user_id):
    blocked = load_json(BLOCKED_FILE)
    return str(user_id) in blocked

def get_blocked_users():
    return list(load_json(BLOCKED_FILE).keys())

# --- مدیریت ادمین‌ها ---
def get_admin_ids():
    data = load_json(ADMINS_FILE)
    return list(map(int, data.keys()))

def add_admin_id(user_id):
    data = load_json(ADMINS_FILE)
    data[str(user_id)] = True
    save_json(ADMINS_FILE, data)

def remove_admin_id(user_id):
    data = load_json(ADMINS_FILE)
    if str(user_id) in data:
        del data[str(user_id)]
        save_json(ADMINS_FILE, data)

def is_admin(user_id):
    data = load_json(ADMINS_FILE)
    return str(user_id) in data
