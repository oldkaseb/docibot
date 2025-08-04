import os
from dotenv import load_dotenv

# فقط برای اجرای محلی، در Railway نیاز نیست
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# لیست آیدی‌های ادمین به‌صورت عددی
ADMIN_IDS = [int(id) for id in os.getenv("ADMIN_IDS", "").split(",") if id]

# در صورت نیاز: آیدی کانال برای توسعه آینده
CHANNEL_ID = os.getenv("CHANNEL_ID")

# مسیر فایل‌های دیتا
USERS_FILE = "data/users.json"
BLOCKED_FILE = "data/blocked.json"
