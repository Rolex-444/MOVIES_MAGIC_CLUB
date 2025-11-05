import os
from os import environ

# Bot information
API_ID = int(environ.get("API_ID", "0"))
API_HASH = environ.get("API_HASH", "")
BOT_TOKEN = environ.get("BOT_TOKEN", "")

# Database
DATABASE_URI = environ.get("DATABASE_URI", "")
DATABASE_NAME = environ.get("DATABASE_NAME", "MovieFilterBot")

# Admin and channels
ADMINS = [int(admin) if admin.isdigit() else admin for admin in environ.get('ADMINS', '').split()]
CHANNELS = [int(ch) if ch.isdigit() else ch for ch in environ.get('CHANNELS', '0').split()]
LOG_CHANNEL = int(environ.get("LOG_CHANNEL", "0"))

# Images
START_IMG = environ.get("START_IMG", "https://telegra.ph/file/d4f88e8df8c19a0c9dbd0.jpg")
PICS = environ.get("PICS", "https://telegra.ph/file/d4f88e8df8c19a0c9dbd0.jpg").split()

# Verification settings
IS_VERIFY = environ.get("IS_VERIFY", "True").lower() in ["true", "yes", "1"]
VERIFY_EXPIRE = int(environ.get("VERIFY_EXPIRE", "21600"))  # ✅ CHANGED: 6 hours (21600) instead of 24 hours
VERIFY_TUTORIAL = environ.get("VERIFY_TUTORIAL", "https://t.me/movies_magic_club3")

# ✅ ADDED: Verification message template
VERIFY_TXT = environ.get("VERIFY_TXT", """
🔐 **Verification Required**

Hello {mention}!

You've used your **{files_sent}/{FREE_FILE_LIMIT} free files** today.
To continue accessing more files, please verify your account.

⏰ **Verification valid for:** 6 hours
💡 **After verification:** Unlimited file access!
🎬 **Our Channel:** @movies_magic_club3

Click the button below to verify:
""")

# Shortlink settings (for verification monetization)
SHORTLINK_URL = environ.get("SHORTLINK_URL", "")  # Example: "arolinks.com"
SHORTLINK_API = environ.get("SHORTLINK_API", "")  # Your API key from shortlink service

# Free limits
FREE_FILE_LIMIT = int(environ.get("FREE_FILE_LIMIT", "5"))

# Premium and referral settings
PREMIUM_POINT = int(environ.get("PREMIUM_POINT", "1500"))
REFER_POINT = int(environ.get("REFER_POINT", "50"))

# Bot settings
PROTECT_CONTENT = environ.get('PROTECT_CONTENT', "False").lower() in ["true", "yes", "1"]
AUTO_DELETE = environ.get('AUTO_DELETE', "True").lower() in ["true", "yes", "1"]
AUTO_DELETE_TIME = int(environ.get("AUTO_DELETE_TIME", "600"))  # 10 minutes

# Search settings
IMDB = environ.get("IMDB", "True").lower() in ["true", "yes", "1"]
SPELL_CHECK = environ.get("SPELL_CHECK", "True").lower() in ["true", "yes", "1"]
MAX_LIST_ELM = int(environ.get("MAX_LIST_ELM", "10"))

# Single character mode
SINGLE_BUTTON = environ.get("SINGLE_BUTTON", "True").lower() in ["true", "yes", "1"]

# Custom file caption
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", "")
BATCH_FILE_CAPTION = environ.get("BATCH_FILE_CAPTION", CUSTOM_FILE_CAPTION)

# Delete channels
DELETE_CHANNELS = [int(dch) if dch.isdigit() else dch for dch in environ.get('DELETE_CHANNELS', '0').split()]

# Stream settings
STREAM_MODE = environ.get('STREAM_MODE', "False").lower() in ["true", "yes", "1"]
NO_PORT = environ.get("NO_PORT", "False").lower() in ["true", "yes", "1"]
APP_NAME = environ.get("APP_NAME", "")

if len(APP_NAME) > 0:
    STREAM_MODE = True

# Port for streaming
PORT = environ.get("PORT", "8080")

# Streaming URL for online video player
STREAM_URL = environ.get("STREAM_URL", "https://elegant-pithivier-bc90f4.netlify.app")

# IMDB settings
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", """
📽️ **{title}**

⭐ Rating: {rating}/10
📅 Release: {release_date}
⏱️ Duration: {runtime} minutes
🎭 Genres: {genres}

📖 Synopsis:
{plot}

Join: @movies_magic_club3
""")

# File caption template
FILE_CAPTION_TEMPLATE = environ.get("FILE_CAPTION_TEMPLATE", """
📁 File Name: {file_name}
📦 Size: {file_size}

🎬 Join: @movies_magic_club3
""")

# Payment channel for UPI verification
PAYMENT_CHANNEL = int(environ.get("PAYMENT_CHANNEL", "-1003037490791"))

# Payment settings
PAYMENT_UPI_ID = environ.get("PAYMENT_UPI_ID", "sivaramanc49@okaxis")
PAYMENT_CHANNEL_LINK = environ.get("PAYMENT_CHANNEL_LINK", "https://t.me/+heQIYvXULRxjOGM1")

# QR code image for UPI payments
UPI_QR_CODE = environ.get("UPI_QR_CODE", "IMG_20251021_083257.jpg")
UPI_ID = environ.get("UPI_ID", "sivaramanc49@okaxis")

# Channel information
YOUR_CHANNEL = environ.get("YOUR_CHANNEL", "@movies_magic_club3")
YOUR_CHANNEL_LINK = environ.get("YOUR_CHANNEL_LINK", "https://t.me/movies_magic_club3")
RARE_VIDEOS_LINK = environ.get("RARE_VIDEOS_LINK", "https://t.me/REAL_TERABOX_PRO_bot")

# ============ FILE STREAMING SETTINGS ============

# BIN_CHANNEL: Private channel to store files for streaming
BIN_CHANNEL = int(environ.get("BIN_CHANNEL", "0"))

# Your Koyeb deployment URL
URL = environ.get("URL", "")

# Worker bots (for bandwidth multiplication)
MULTI_TOKEN1 = environ.get("MULTI_TOKEN1", "")
MULTI_TOKEN2 = environ.get("MULTI_TOKEN2", "")
MULTI_TOKEN3 = environ.get("MULTI_TOKEN3", "")
MULTI_TOKEN4 = environ.get("MULTI_TOKEN4", "")
MULTI_TOKEN5 = environ.get("MULTI_TOKEN5", "")

# Get all available tokens
def get_all_tokens():
    tokens = []
    for i in range(1, 11):  # Support up to 10 worker bots
        token = environ.get(f"MULTI_TOKEN{i}", "")
        if token:
            tokens.append(token)
    return tokens if tokens else [BOT_TOKEN]

ALL_TOKENS = get_all_tokens()
