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
VERIFY_EXPIRE = int(environ.get("VERIFY_EXPIRE", "86400"))  # 24 hours in seconds
VERIFY_TUTORIAL = environ.get("VERIFY_TUTORIAL", "https://t.me/movies_magic_club3")

# Shortlink settings (for verification monetization)
SHORTLINK_URL = environ.get("SHORTLINK_URL", "")
SHORTLINK_API = environ.get("SHORTLINK_API", "")

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

# IMDB settings
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", """
<b>Title:</b> {title}
<b>Rating:</b> ⭐ {rating}/10
<b>Release:</b> {release_date}
<b>Duration:</b> {runtime} minutes
<b>Genres:</b> {genres}

<b>Synopsis:</b> {plot}
""")

# File caption template
FILE_CAPTION_TEMPLATE = environ.get("FILE_CAPTION_TEMPLATE", """
<b>📁 File Name:</b> <code>{file_name}</code>

<b>📦 Size:</b> {file_size}

<b>Join:</b> @movies_magic_club3
""")

# Payment channel for UPI verification
PAYMENT_CHANNEL = int(environ.get("PAYMENT_CHANNEL", "-1003037490791"))

# QR code image for UPI payments
UPI_QR_CODE = environ.get("UPI_QR_CODE", "IMG_20251021_083257.jpg")
UPI_ID = environ.get("UPI_ID", "sivaramanc49@okaxis")
