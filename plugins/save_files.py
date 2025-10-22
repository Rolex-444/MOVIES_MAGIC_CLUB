from pyrogram import Client, filters
from info import CHANNELS, DELETE_CHANNELS, DATABASE_URI, DATABASE_NAME
import logging
import re
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

# Initialize MongoDB directly
try:
    mongo_client = AsyncIOMotorClient(DATABASE_URI)
    db = mongo_client[DATABASE_NAME]
    files_collection = db.files
except Exception as e:
    logger.error(f"Database connection error: {e}")

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

@Client.on_message(filters.channel) # REMOVED "& filters.incoming" to catch ALL channel messages
async def save_files(client, message):
    """Save files from storage channels (catches both incoming and copied messages)"""
    
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
        file_unique_id = media.file_unique_id  # ✅ ADDED: Unique file identifier
        file_ref = getattr(media, 'file_ref', '')
        file_name = getattr(media, 'file_name', '') or message.caption or 'Untitled'
        file_size = media.file_size
        file_type = message.media.value if message.media else 'document'
        mime_type = getattr(media, 'mime_type', 'unknown')  # ✅ ADDED: MIME type for better handling
        
        # Check if file already exists in database (avoid duplicates)
        existing = await files_collection.find_one({'file_id': file_id})
        if existing:
            logger.info(f"⚠️ File already in database: {file_name[:30]}...")
            return
        
        # Prepare file document for MongoDB
        file_document = {
            'file_id': file_id,
            'file_unique_id': file_unique_id,  # ✅ ADDED: For better file tracking
            'file_ref': file_ref,
            'file_name': file_name,
            'file_size': file_size,
            'file_type': file_type,
            'mime_type': mime_type,  # ✅ ADDED: MIME type
            'caption': message.caption or '',
            'chat_id': message.chat.id,
            'message_id': message.id
        }
        
        # Insert directly into MongoDB
        result = await files_collection.insert_one(file_document)
        
        if result.inserted_id:
            logger.info(f"✅ Auto-saved: {file_name[:50]} (ID: {file_id[:20]}...)")
            
    except Exception as e:
        logger.error(f"❌ Error saving file: {e}")
        
