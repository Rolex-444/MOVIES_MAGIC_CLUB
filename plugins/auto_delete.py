from pyrogram import Client, filters, enums
from database.database import Database
from info import DELETE_CHANNELS, ADMINS
import logging

logger = logging.getLogger(__name__)
db = Database()


@Client.on_message(filters.channel)  # Listen to ALL channels
async def auto_delete_file(client, message):
    """Auto-delete files forwarded to DELETE_CHANNELS"""
    
    # Check if message is from DELETE_CHANNELS
    if message.chat.id not in DELETE_CHANNELS:
        return  # Not a delete channel, ignore
    
    logger.info(f"🔍 Message received in DELETE_CHANNEL: {message.chat.id}")
    
    # Check if message has media
    if not message.media:
        logger.info(f"Non-media message in DELETE_CHANNELS")
        return
    
    # Get file details
    media = message.document or message.video or message.audio
    if not media:
        logger.info(f"No media found in message")
        return
    
    file_id = media.file_id
    file_name = getattr(media, 'file_name', 'Unknown')
    
    logger.info(f"🗑️ File forwarded to DELETE_CHANNELS: {file_name} (file_id: {file_id})")
    
    try:
        # Step 1: Get file info from database
        file_data = await db.get_file_by_file_id(file_id)
        
        if not file_data:
            await message.delete()
            logger.warning(f"⚠️ File {file_name} not found in database, deleted from DELETE_CHANNELS only")
            return
        
        original_channel = file_data.get('channel_id')
        original_message_id = file_data.get('message_id')
        
        logger.info(f"Found file in DB - Channel: {original_channel}, Msg ID: {original_message_id}")
        
        # Step 2: Delete from MongoDB database
        delete_result = await db.delete_file_by_file_id(file_id)
        db_deleted = delete_result.deleted_count if delete_result else 0
        
        logger.info(f"Database delete result: {db_deleted} records deleted")
        
        # Step 3: Delete from original storage channel
        channel_deleted = False
        if original_channel and original_message_id:
            try:
                await client.delete_messages(
                    chat_id=original_channel,
                    message_ids=original_message_id
                )
                channel_deleted = True
                logger.info(f"✅ Deleted from storage channel: {original_channel}")
            except Exception as e:
                logger.error(f"❌ Error deleting from storage channel: {e}")
        
        # Step 4: Delete from DELETE_CHANNELS
        try:
            await message.delete()
            logger.info(f"✅ Deleted from DELETE_CHANNELS")
        except Exception as e:
            logger.error(f"❌ Error deleting from DELETE_CHANNELS: {e}")
        
        # Log result
        if db_deleted > 0 and channel_deleted:
            logger.info(f"✅✅✅ FULL DELETE SUCCESS: {file_name}")
        elif db_deleted > 0:
            logger.warning(f"⚠️ PARTIAL DELETE (DB only): {file_name}")
        else:
            logger.error(f"❌ DELETE FAILED: {file_name}")
            
    except Exception as e:
        logger.error(f"❌ Auto-delete error for {file_name}: {e}")
        try:
            await message.delete()
        except:
            pass
    
