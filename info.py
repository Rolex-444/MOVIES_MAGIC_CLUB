import os
from os import environ
import re
import time

# Bot Configuration
API_ID = int(environ.get("API_ID", "12345678"))
API_HASH = environ.get("API_HASH", "your_api_hash_here")
BOT_TOKEN = environ.get("BOT_TOKEN", "your_bot_token_here")

# Database Configuration
DATABASE_URI = environ.get("DATABASE_URI", "mongodb+srv://username:password@cluster.mongodb.net/")
DATABASE_NAME = environ.get("DATABASE_NAME", "MovieFilterBot")

# Channels & Admin
id_pattern = re.compile(r'^.\d+$')
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '-100').split()]
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '').split()]
LOG_CHANNEL = int(environ.get("LOG_CHANNEL", "0"))
SUPPORT_CHAT = environ.get("SUPPORT_CHAT", "movies_magic_club3")

# Owner
OWNER_USERNAME = "Siva9789"

# Force Subscribe
FORCE_SUB_CHANNEL = int(environ.get("FORCE_SUB_CHANNEL", "0"))
FORCE_SUB_CHANNEL2 = int(environ.get("FORCE_SUB_CHANNEL2", "0"))

# Verification System
IS_VERIFY = bool(environ.get("IS_VERIFY", True))
VERIFY_TUTORIAL = environ.get("VERIFY_TUTORIAL", "https://t.me/movies_magic_club3")
SHORTLINK_API = environ.get("SHORTLINK_API", "")
SHORTLINK_URL = environ.get("SHORTLINK_URL", "")
VERIFY_EXPIRE = int(environ.get("VERIFY_EXPIRE", "86400"))  # 24 hours in seconds

# Premium Features
PREMIUM_POINT = int(environ.get("PREMIUM_POINT", "1500"))
REFER_POINT = int(environ.get("REFER_POINT", "50"))

# Auto Delete
AUTO_DELETE = bool(environ.get("AUTO_DELETE", True))
AUTO_DELETE_TIME = int(environ.get("AUTO_DELETE_TIME", "600"))  # 10 minutes

# Stream Settings
STREAM_MODE = bool(environ.get("STREAM_MODE", False))
PORT = int(environ.get("PORT", "8080"))

# Rename Settings
RENAME_MODE = bool(environ.get("RENAME_MODE", True))

# Other Settings
SINGLE_BUTTON = bool(environ.get("SINGLE_BUTTON", False))
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", "")
BATCH_FILE_CAPTION = environ.get("BATCH_FILE_CAPTION", "")
IMDB = bool(environ.get("IMDB", True))
SPELL_CHECK = bool(environ.get("SPELL_CHECK", True))
MAX_B_TN = int(environ.get("MAX_B_TN", "10"))
MAX_LIST_ELM = int(environ.get("MAX_LIST_ELM", "5"))
INDEX_REQ_CHANNEL = int(environ.get("INDEX_REQ_CHANNEL", LOG_CHANNEL))
FILE_STORE_CHANNEL = [int(ch) for ch in (environ.get('FILE_STORE_CHANNEL', '')).split()]
MELCOW_NEW_USERS = bool(environ.get("MELCOW_NEW_USERS", True))
PROTECT_CONTENT = bool(environ.get("PROTECT_CONTENT", False))
PUBLIC_FILE_STORE = bool(environ.get("PUBLIC_FILE_STORE", True))

# Pics
PICS = (environ.get('PICS', 'https://telegra.ph/file/7e56d907542396289fee4.jpg https://telegra.ph/file/9aa8dd372f4739fe02d85.jpg')).split()
START_IMG = environ.get("START_IMG", "https://i.ibb.co/bPz7QRh/file-15.jpg")

# Bot Info
BOT_START_TIME = time.time()
