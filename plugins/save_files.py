from pyrogram import Client, filters
from database.database import Database
from info import CHANNELS, DELETE_CHANNELS  # Import DELETE_CHANNELS
import logging

logger = logging.getLogger(__name__)
db = Database()


@Client.on_message(filters.channel & filters.chat(CHANNELS))  # Only CHANNELS, not DELETE_CHANNELS
async def save_files(client, message):
    """Save files from storage channels only (exclude DELETE_CHANNELS)"""
    
    # Double check - skip if it's a delete channel
    if message.chat.id in DELETE_CHANNELS:
        logger.info(f"Skipping file from DELETE_CHANNEL: {message.chat.id}")
        return
    
    # Check if message has media
    if not message.media:
        return
    
    # Get file details
    media = message.document or message.video or message.audio
    if not media:
        return
    
    file_id = media.file_id
    file_name = getattr(media, 'file_name', 'Unknown')
    file_size = media.file_size
    
    # Prepare file data
    file_data = {
        'file_id': file_id,
        'file_name': file_name,
        'file_size': file_size,
        'channel_id': message.chat.id,
        'message_id': message.id,
        'caption': message.caption or ''
    }
    
    # Save to database
    try:
        await db.add_file(file_data)
        logger.info(f"✅ Saved file: {file_name}")
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        
