import json
import os

DB_FILE = "data/users.json"

def get_all_users():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_user(user_id, user_data):
    users = get_all_users()
    users[str(user_id)] = user_data
    with open(DB_FILE, "w") as f:
        json.dump(users, f, indent=2)
