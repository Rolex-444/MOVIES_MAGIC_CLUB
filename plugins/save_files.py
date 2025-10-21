from pyrogram import Client, filters
from database.database import Database
from info import CHANNELS, DELETE_CHANNELS
import logging
import re

logger = logging.getLogger(__name__)

# Initialize database
db = Database()

# Robust parsing that handles multiple formats
def parse_channels(channel_var):
    """Parse channels from string, handling multiple formats"""
    if not channel_var:
        return []
    
    # Convert to string
    channel_str = str(channel_var)
    
    # Remove brackets, quotes, and whitespace
    channel_str = re.sub(r'[\[\]\'\"]', '', channel_str)
    
    # Split by space or comma
    channels = re.split(r'[\s,]+', channel_str.strip())
    
    # Convert to integers, skip invalid
    result = []
    for ch in channels:
        ch = ch.strip()
        if ch and ch.lstrip('-').isdigit():
            try:
                result.append(int(ch))
            except ValueError:
                pass
    
    return result

# Parse channels
try:
    SAVE_CHANNELS = parse_channels(CHANNELS)
    DELETE_CHANNEL_LIST = parse_channels(DELETE_CHANNELS)
except Exception as e:
    logger.error(f"Error parsing channels: {e}")
    SAVE_CHANNELS = []
    DELETE_CHANNEL_LIST = []

logger.info(f"✅ Auto-save enabled for channels: {SAVE_CHANNELS}")
logger.info(f"⛔ Delete channels (skip save): {DELETE_CHANNEL_LIST}")


@Client.on_message(filters.channel & filters.incoming)
async def save_files(client, message):
    """Save files from storage channels only (exclude DELETE_CHANNELS)"""
    
    # Check if from a monitored channel
    if message.chat.id not in SAVE_CHANNELS:
        return
    
    # Double check - skip if it's a delete channel
    if message.chat.id in DELETE_CHANNEL_LIST:
        logger.info(f"⛔ Skipping file from DELETE_CHANNEL: {message.chat.id}")
        return
    
    # Check if message has media
    if not message.media:
        return
    
    # Get file details
    media = message.document or message.video or message.audio
    if not media:
        return
    
    try:
        file_id = media.file_id
        file_ref = getattr(media, 'file_ref', '')
        file_name = getattr(media, 'file_name', '') or message.caption or 'Untitled'
        file_size = media.file_size
        file_type = message.media.value if message.media else 'document'
        
        # Save using your Database class
        # Note: Check what method your Database class has
        # It might be save_file(), add_file(), insert(), etc.
        result = await db.save_file(file_id, file_name, file_type, file_size, message.caption or '')
        
        if result:
            logger.info(f"✅ Auto-saved: {file_name[:50]} (ID: {file_id[:20]}...)")
        
    except Exception as e:
        logger.error(f"❌ Error saving file: {e}")
        
