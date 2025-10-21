from pyrogram import Client, filters
from database.database import Database
from info import CHANNELS, DELETE_CHANNELS
import logging

logger = logging.getLogger(__name__)

# Initialize database
db = Database()

# Convert CHANNELS to list of integers
try:
    SAVE_CHANNELS = [int(ch) for ch in str(CHANNELS).split()] if CHANNELS else []
    DELETE_CHANNEL_LIST = [int(ch) for ch in str(DELETE_CHANNELS).split()] if DELETE_CHANNELS else []
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
        
        # Save to database using db.save_file() method
        result = await db.save_file(file_id, file_name, file_type, file_size, message.caption or '')
        
        if result:
            logger.info(f"✅ Auto-saved: {file_name[:50]} (ID: {file_id[:20]}...)")
        
    except Exception as e:
        logger.error(f"❌ Error saving file: {e}")
    
