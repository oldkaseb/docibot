import json
import os

USERS_FILE = "data/users.json"
ADMINS_FILE = "data/admins.json"
BLOCKED_FILE = "data/blocked.json"

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def get_all_users():
    return load_json(USERS_FILE)

def add_user(user_id, user_data):
    users = load_json(USERS_FILE)
    users[str(user_id)] = user_data
    save_json(USERS_FILE, users)

def get_admin_ids():
    data = load_json(ADMINS_FILE)
    return data.get("admins", [])

def add_admin_id(user_id):
    data = load_json(ADMINS_FILE)
    if "admins" not in data:
        data["admins"] = []
    if user_id not in data["admins"]:
        data["admins"].append(user_id)
    save_json(ADMINS_FILE, data)

def remove_admin_id(user_id):
    data = load_json(ADMINS_FILE)
    if "admins" in data and user_id in data["admins"]:
        data["admins"].remove(user_id)
        save_json(ADMINS_FILE, data)

def get_blocked_users():
    return load_json(BLOCKED_FILE).get("blocked", [])

def add_blocked_user(user_id):
    data = load_json(BLOCKED_FILE)
    if "blocked" not in data:
        data["blocked"] = []
    if user_id not in data["blocked"]:
        data["blocked"].append(user_id)
    save_json(BLOCKED_FILE, data)

def remove_blocked_user(user_id):
    data = load_json(BLOCKED_FILE)
    if "blocked" in data and user_id in data["blocked"]:
        data["blocked"].remove(user_id)
        save_json(BLOCKED_FILE, data)

def is_user_blocked(user_id):
    return user_id in get_blocked_users()

# Shortcuts for compatibility
block_user = add_blocked_user
unblock_user = remove_blocked_user
