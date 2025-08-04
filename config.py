import os

# توکن ربات از محیط (مثلاً Railway)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# لیست آیدی ادمین‌ها به‌صورت عددی
# مقدار محیطی باید به‌شکل: 123456789,987654321 باشد
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))
