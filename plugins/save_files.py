from pyrogram import Client, filters, enums
from database.database import Database
import logging

logger = logging.getLogger(__name__)
db = Database()

@Client.on_message(filters.channel & filters.media)
async def save_file_to_db(client, message):
    """Automatically save files from storage channel to database"""
    
    # Get file details
    media = message.document or message.video or message.audio
    
    if not media:
        return
    
    # Extract file information
    file_id = media.file_id
    file_name = getattr(media, 'file_name', f"File_{file_id[:8]}")
    file_size = getattr(media, 'file_size', 0)
    file_type = "document" if message.document else "video" if message.video else "audio"
    
    # Caption if available
    caption = message.caption if message.caption else ""
    
    # Save to database
    try:
        file_data = {
            'file_id': file_id,
            'file_name': file_name,
            'file_size': file_size,
            'file_type': file_type,
            'caption': caption,
            'channel_id': message.chat.id,
            'message_id': message.id
        }
        
        await db.add_file(file_data)
        logger.info(f"✅ Saved file: {file_name}")
        
    except Exception as e:
        logger.error(f"❌ Error saving file: {e}")


@Client.on_message(filters.command("total") & filters.private)
async def total_files(client, message):
    """Check total files in database"""
    try:
        total = await db.total_files()
        await message.reply(
            f"📊 <b>Database Statistics</b>\n\n"
            f"📁 Total Files: {total}\n\n"
            f"Join: @movies_magic_club3",
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        await message.reply(f"❌ Error: {e}")
