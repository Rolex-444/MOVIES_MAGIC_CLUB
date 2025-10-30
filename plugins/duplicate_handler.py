"""
Duplicate File Handler - Automatically removes duplicate files
When same filename + size is saved, deletes the old one and keeps new one
"""

from pyrogram import Client, filters
from database.database import Database
from info import ADMINS, LOG_CHANNEL
import logging

logger = logging.getLogger(__name__)

db = Database()


async def check_and_remove_duplicate(file_name, file_size, file_id, new_file_unique_id):
    """
    Check if file with same name and size exists
    If yes, delete old one and return True
    """
    try:
        # Search for existing file with same name and size
        existing_files = await db.find_duplicate_files(file_name, file_size)
        
        if existing_files:
            for old_file in existing_files:
                old_file_id = old_file.get('_id')
                old_unique_id = old_file.get('file_unique_id')
                
                # Don't delete if it's the exact same file (same unique_id)
                if old_unique_id == new_file_unique_id:
                    logger.info(f"⚠️ Same file uploaded again: {file_name}")
                    return False, "same_file"
                
                # Delete the old duplicate
                deleted = await db.delete_file(old_file_id)
                
                if deleted:
                    logger.info(f"🗑️ Deleted duplicate: {file_name} (ID: {old_file_id})")
                    return True, old_file_id
        
        return False, None
        
    except Exception as e:
        logger.error(f"Error checking duplicates: {e}")
        return False, None


@Client.on_message(filters.document | filters.video | filters.audio)
async def handle_file_save_with_duplicate_check(client, message):
    """
    This handler runs when files are saved to database
    It checks for duplicates and removes them
    """
    # Only process files from connected channels
    if message.chat.type not in ["channel", "supergroup"]:
        return
    
    # Get file info
    media = message.document or message.video or message.audio
    
    if not media:
        return
    
    file_name = media.file_name or "Unknown"
    file_size = media.file_size
    file_id = media.file_id
    file_unique_id = media.file_unique_id
    
    # Check for duplicates BEFORE saving
    is_duplicate, old_id = await check_and_remove_duplicate(
        file_name, 
        file_size, 
        file_id,
        file_unique_id
    )
    
    if is_duplicate == "same_file":
        logger.info(f"⚠️ Exact same file, skipping: {file_name}")
        return
    
    # Send notification if duplicate was deleted
    if is_duplicate:
        try:
            # Notify in log channel
            if LOG_CHANNEL:
                notification = f"""
🗑️ **Duplicate File Removed**

📁 **File Name:** `{file_name}`
📦 **Size:** {file_size} bytes
🆔 **Old ID:** `{old_id}`
✅ **Action:** Deleted old, saved new version

**New file saved successfully!**
"""
                await client.send_message(LOG_CHANNEL, notification)
        except Exception as e:
            logger.error(f"Error sending notification: {e}")


logger.info("✅ DUPLICATE HANDLER PLUGIN LOADED")
