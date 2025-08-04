import json
import os
from datetime import datetime

DB_PATH = "data/users.json"
REPLY_STATE = {}
BLOCKED_USERS = set()

if not os.path.exists("data"):
    os.makedirs("data")
if not os.path.isfile(DB_PATH):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump({}, f)

def load_db():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(data):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_user(user):
    db = load_db()
    if str(user.id) not in db:
        db[str(user.id)] = {
            "full_name": user.full_name,
            "username": user.username,
            "id": user.id,
            "joined_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_db(db)

def save_message(user):
    add_user(user)

def get_all_users():
    return load_db()

def is_blocked(user_id):
    return user_id in BLOCKED_USERS

def block_user(user_id):
    BLOCKED_USERS.add(user_id)

def unblock_user(user_id):
    BLOCKED_USERS.discard(user_id)

def set_reply_state(admin_id, user_id):
    REPLY_STATE[admin_id] = user_id

def get_reply_state(admin_id):
    return REPLY_STATE.get(admin_id)

def clear_reply_state(admin_id):
    REPLY_STATE.pop(admin_id, None)