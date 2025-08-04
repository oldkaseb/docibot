import os
from dotenv import load_dotenv

# فقط برای اجرای محلی
load_dotenv()

# توکن ربات
BOT_TOKEN = os.getenv("BOT_TOKEN")

# لیست آیدی‌های عددی ادمین
from config import ADMIN_IDS
admin_ids = ADMIN_IDS

# مسیر فایل‌های داده
USERS_FILE = "data/users.json"
BLOCKED_FILE = "data/blocked.json"
