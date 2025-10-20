from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.database import Database
from info import ADMINS, CHANNELS
import asyncio

db = Database()

@Client.on_message(filters.command("index") & filters.user(ADMINS))
async def index_files_command(client, message):
    """Index files from channels"""
    
    if len(message.command) < 2:
        await message.reply(
            "Usage: /index <channel_id> [skip_number]\n\n"
            "Example: /index -1001234567890 100"
        )
        return
    
    try:
        channel_id = int(message.command[1])
        skip = int(message.command[2]) if len(message.command) > 2 else 0
        
        status = await message.reply("Starting indexing...")
        
        indexed = 0
        duplicate = 0
        
        async for msg in client.iter_history(channel_id, offset=skip):
            media = msg.document or msg.video or msg.audio
            
            if media:
                file_data = {
                    '_id': msg.id,
                    'file_id': media.file_id,
                    'file_name': getattr(media, 'file_name', 'Unknown'),
                    'file_size': getattr(media, 'file_size', 0),
                    'caption': msg.caption if msg.caption else "",
                    'channel_id': channel_id,
                    'message_id': msg.id
                }
                
                try:
                    await db.add_file(file_data)
                    indexed += 1
                except:
                    duplicate += 1
                
                if indexed % 100 == 0:
                    try:
                        await status.edit(
                            f"Indexing...\n\n"
                            f"✅ Indexed: {indexed}\n"
                            f"⚠️ Duplicate: {duplicate}"
                        )
                    except:
                        pass
        
        await status.edit(
            f"✅ <b>Indexing Completed!</b>\n\n"
            f"📁 <b>Total Indexed:</b> {indexed}\n"
            f"⚠️ <b>Duplicates:</b> {duplicate}"
        )
        
    except Exception as e:
        await message.reply(f"Error: {e}")


@Client.on_message(filters.command("total") & filters.user(ADMINS))
async def total_files_command(client, message):
    """Show total indexed files"""
    
    total = await db.total_files_count()
    await message.reply(f"📁 <b>Total Files:</b> {total}")
