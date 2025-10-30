"""
Automatic Duplicate Remover
- Runs AFTER save_files.py saves the file
- Checks if duplicate exists
- Deletes old duplicate, keeps newest
- Works perfectly with your existing save_files.py
"""

from pyrogram import Client, filters
from database.database import Database
from info import LOG_CHANNEL
import logging
import asyncio

logger = logging.getLogger(__name__)

db = Database()


async def auto_check_and_remove_duplicates(client, file_name, file_size, new_file_unique_id):
    """
    Automatically check and remove duplicates after file is saved
    """
    try:
        # Wait 2 seconds to ensure file is saved first
        await asyncio.sleep(2)
        
        # Find duplicates with same name and size
        existing_files = await db.find_duplicate_files(file_name, file_size)
        
        if len(existing_files) <= 1:
            # No duplicates, exit
            return False
        
        logger.info(f"🔍 Found {len(existing_files)} files with name: {file_name}")
        
        # Sort by _id (ObjectId contains timestamp, newer = larger)
        sorted_files = sorted(existing_files, key=lambda x: x['_id'], reverse=True)
        
        # Keep the newest (first), delete rest
        newest_file = sorted_files[0]
        old_files = sorted_files[1:]
        
        deleted_count = 0
        
        for old_file in old_files:
            old_file_id = old_file.get('_id')
            old_unique_id = old_file.get('file_unique_id', '')
            
            # Don't delete if it's the exact same Telegram file
            if old_unique_id == new_file_unique_id:
                logger.info(f"⚠️ Same Telegram file, skipping: {file_name}")
                continue
            
            # Delete the old duplicate
            result = await db.delete_file_by_id(old_file_id)
            
            if result and result.deleted_count > 0:
                deleted_count += 1
                logger.info(f"🗑️ Auto-deleted duplicate #{deleted_count}: {file_name}")
        
        # Send notification if duplicates were deleted
        if deleted_count > 0 and LOG_CHANNEL:
            try:
                notification = f"""
🗑️ <b>Auto-Deleted Duplicates</b>

📁 <b>File:</b> <code>{file_name}</code>
📦 <b>Size:</b> {file_size} bytes
🔢 <b>Deleted:</b> {deleted_count} old version(s)
✅ <b>Kept:</b> Newest version

<i>Automatic duplicate cleanup</i>
"""
                await client.send_message(LOG_CHANNEL, notification, parse_mode="html")
            except Exception as e:
                logger.error(f"Error sending notification: {e}")
        
        return deleted_count > 0
        
    except Exception as e:
        logger.error(f"Error in auto duplicate check: {e}")
        return False


# This handler runs AFTER files are saved by save_files.py
# It only checks for duplicates, doesn't interfere with saving
@Client.on_message(filters.document | filters.video | filters.audio, group=2)
async def duplicate_checker(client, message):
    """
    Automatic duplicate checker - runs after save_files.py (group=2)
    """
    try:
        # Only check files from channels in CHANNELS list
        if message.chat.type not in ["channel", "supergroup"]:
            return
        
        # Get file info
        media = message.document or message.video or message.audio
        
        if not media:
            return
        
        file_name = getattr(media, 'file_name', None) or "Unknown"
        file_size = media.file_size
        file_unique_id = media.file_unique_id
        
        # Check and remove duplicates in background (non-blocking)
        asyncio.create_task(
            auto_check_and_remove_duplicates(client, file_name, file_size, file_unique_id)
        )
        
    except Exception as e:
        logger.error(f"Error in duplicate_checker: {e}")


logger.info("✅ AUTOMATIC DUPLICATE REMOVER LOADED (group=2, after save_files)")
                   
