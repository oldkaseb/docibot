import os
from dotenv import load_dotenv

# فقط برای اجرای محلی
load_dotenv()

# توکن ربات
BOT_TOKEN = os.getenv("BOT_TOKEN")

# لیست آیدی‌های عددی ادمین
ADMIN_IDS = [int(id) for id in os.getenv("ADMIN_IDS", "").split(",") if id]

# مسیر فایل‌های داده
USERS_FILE = "data/users.json"
BLOCKED_FILE = "data/blocked.json"
