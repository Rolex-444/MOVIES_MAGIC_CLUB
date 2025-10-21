from pyrogram import Client, filters, enums
from database.database import Database
from info import DELETE_CHANNELS, ADMINS
import logging

logger = logging.getLogger(__name__)
db = Database()


@Client.on_message(filters.channel, group=-1)  # Higher priority (runs first)
async def auto_delete_file(client, message):
    """Auto-delete files forwarded to DELETE_CHANNELS - RUNS FIRST"""
    
    # Check if message is from DELETE_CHANNELS
    if message.chat.id not in DELETE_CHANNELS:
        return  # Not a delete channel, let other handlers process it
    
    logger.info(f"🔍 DELETE CHANNEL DETECTED: {message.chat.id}")
    
    # Check if message has media
    if not message.media:
        logger.info(f"Non-media message in DELETE_CHANNELS")
        return
    
    # Get file details
    media = message.document or message.video or message.audio
    if not media:
        logger.info(f"No document/video/audio found")
        return
    
    file_id = media.file_id
    file_name = getattr(media, 'file_name', 'Unknown')
    
    logger.info(f"🗑️ DELETING: {file_name} (file_id: {file_id})")
    
    try:
        # Step 1: Get file info from database
        file_data = await db.get_file_by_file_id(file_id)
        
        if not file_data:
            await message.delete()
            logger.warning(f"⚠️ File not in DB, deleted from channel only")
            message.stop_propagation()  # Stop other handlers
            return
        
        original_channel = file_data.get('channel_id')
        original_message_id = file_data.get('message_id')
        
        logger.info(f"Found in DB - Channel: {original_channel}, Msg: {original_message_id}")
        
        # Step 2: Delete from MongoDB
        delete_result = await db.delete_file_by_file_id(file_id)
        db_deleted = delete_result.deleted_count if delete_result else 0
        
        logger.info(f"DB delete: {db_deleted} records")
        
        # Step 3: Delete from storage channel
        channel_deleted = False
        if original_channel and original_message_id:
            try:
                await client.delete_messages(chat_id=original_channel, message_ids=original_message_id)
                channel_deleted = True
                logger.info(f"✅ Deleted from storage channel")
            except Exception as e:
                logger.error(f"❌ Storage channel error: {e}")
        
        # Step 4: Delete from DELETE_CHANNELS
        try:
            await message.delete()
            logger.info(f"✅ Deleted from DELETE_CHANNELS")
        except Exception as e:
            logger.error(f"❌ DELETE_CHANNELS error: {e}")
        
        # Log final result
        if db_deleted > 0 and channel_deleted:
            logger.info(f"✅✅✅ FULL DELETE SUCCESS: {file_name}")
        elif db_deleted > 0:
            logger.warning(f"⚠️ PARTIAL DELETE (DB only): {file_name}")
        else:
            logger.error(f"❌ DELETE FAILED: {file_name}")
        
        # Stop message from reaching other handlers (like save_files)
        message.stop_propagation()
            
    except Exception as e:
        logger.error(f"❌ Exception: {e}")
        try:
            await message.delete()
        except:
            pass
        message.stop_propagation()
        
