from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.database import Database
from info import ADMINS
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)
db = Database()


@Client.on_message(filters.command("del") & filters.user(ADMINS))
async def delete_file_search(client, message):
    """
    Admin command to delete files
    Usage: /del <filename>
    Example: /del The life list
    """
    
    if len(message.command) < 2:
        await message.reply(
            "<b>❌ Usage:</b> /del <filename>\n\n"
            "<b>Example:</b> /del Meg 2",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    # Get search query
    search = message.text.split(None, 1)[1]
    
    # Search for files
    try:
        result = await db.search_files(search)
        
        if isinstance(result, tuple):
            files, total = result
        else:
            files = result
            
    except Exception as e:
        await message.reply(f"❌ Error: {e}", parse_mode=enums.ParseMode.HTML)
        return
    
    if not files:
        await message.reply(
            f"❌ No files found for: <code>{search}</code>",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    # Show files with delete buttons
    btn = []
    for file in files[:15]:  # Limit to 15
        file_id = str(file.get('_id', ''))
        file_name = file.get('file_name', 'Unknown')[:50]
        
        btn.append([InlineKeyboardButton(
            f"🗑️ {file_name}...",
            callback_data=f"DEL_{file_id}"
        )])
    
    btn.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_del")])
    
    await message.reply(
        f"<b>Found {len(files)} files:</b>\n\n"
        f"Click to delete ⬇️",
        reply_markup=InlineKeyboardMarkup(btn),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex(r"^DEL_"))
async def confirm_delete_file(client, query):
    """Confirm and delete file"""
    
    file_id = query.data.replace("DEL_", "")
    
    try:
        # Get file data
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
        channel_status = "❓"
        if channel_id and message_id:
            try:
                await client.delete_messages(chat_id=channel_id, message_ids=message_id)
                channel_status = "✅"
            except Exception as e:
                channel_status = f"❌ ({e})"
        
        await query.message.edit_text(
            f"<b>✅ FILE DELETED!</b>\n\n"
            f"<b>File:</b> <code>{file_name}</code>\n\n"
            f"• Database: ✅\n"
            f"• Channel: {channel_status}",
            parse_mode=enums.ParseMode.HTML
        )
        await query.answer("Deleted!", show_alert=False)
        
    except Exception as e:
        logger.error(f"Delete error: {e}")
        await query.answer(f"Error: {e}", show_alert=True)


@Client.on_callback_query(filters.regex("^cancel_del$"))
async def cancel_delete(client, query):
    """Cancel deletion"""
    await query.message.delete()
    await query.answer("Cancelled!", show_alert=False)
