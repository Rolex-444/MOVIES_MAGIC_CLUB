from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.database import Database
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)
db = Database()


@Client.on_message(filters.command("del") & filters.private)  # Removed filters.user(ADMINS) for testing
async def delete_file_search(client, message):
    """Delete files command - WORKS FOR ANYONE (testing)"""
    
    logger.info(f"🔍 /del command received from user: {message.from_user.id}")
    
    if len(message.command) < 2:
        await message.reply(
            "<b>❌ Usage:</b> /del <filename>\n\n"
            "<b>Example:</b> /del Meg 2\n\n"
            f"<b>Your ID:</b> <code>{message.from_user.id}</code>",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    search = message.text.split(None, 1)[1]
    
    logger.info(f"Searching for: {search}")
    
    # Search for files
    try:
        result = await db.search_files(search)
        
        if isinstance(result, tuple):
            files, total = result
        else:
            files = result
        
        logger.info(f"Found {len(files)} files")
            
    except Exception as e:
        logger.error(f"Search error: {e}")
        await message.reply(f"❌ Error: {e}", parse_mode=enums.ParseMode.HTML)
        return
    
    if not files:
        await message.reply(
            f"❌ No files found for: <code>{search}</code>",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    # Show files
    btn = []
    for file in files[:10]:
        file_id = str(file.get('_id', ''))
        file_name = file.get('file_name', 'Unknown')[:40]
        
        btn.append([InlineKeyboardButton(
            f"🗑️ {file_name}",
            callback_data=f"DEL_{file_id}"
        )])
    
    btn.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_del")])
    
    await message.reply(
        f"<b>Found {len(files)} files:</b>\n\nClick to delete",
        reply_markup=InlineKeyboardMarkup(btn),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex(r"^DEL_"))
async def confirm_delete_file(client, query):
    """Delete file"""
    
    file_id = query.data.replace("DEL_", "")
    
    try:
        if len(file_id) == 24:
            mongo_id = ObjectId(file_id)
        else:
            mongo_id = file_id
        
        file_data = await db.get_file(mongo_id)
        
        if not file_data:
            await query.answer("❌ File not found!", show_alert=True)
            return
        
        file_name = file_data.get('file_name', 'Unknown')
        channel_id = file_data.get('channel_id')
        message_id = file_data.get('message_id')
        
        # Delete from database
        await db.delete_file(mongo_id)
        
        # Delete from channel
        if channel_id and message_id:
            try:
                await client.delete_messages(chat_id=channel_id, message_ids=message_id)
                channel_status = "✅"
            except:
                channel_status = "❌"
        else:
            channel_status = "❓"
        
        await query.message.edit_text(
            f"<b>✅ FILE DELETED!</b>\n\n"
            f"<code>{file_name}</code>\n\n"
            f"• Database: ✅\n"
            f"• Channel: {channel_status}",
            parse_mode=enums.ParseMode.HTML
        )
        await query.answer("Deleted!")
        
    except Exception as e:
        logger.error(f"Delete error: {e}")
        await query.answer(f"Error: {e}", show_alert=True)


@Client.on_callback_query(filters.regex("^cancel_del$"))
async def cancel_delete(client, query):
    await query.message.delete()
    await query.answer("Cancelled!")
                               
