from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.database import Database
from database.verify import VerifyDB
from bson import ObjectId
from info import ADMINS
import logging

logger = logging.getLogger(__name__)
db = Database()
verify_db = VerifyDB()


@Client.on_message(filters.command("start") & filters.private & filters.regex(r"^/start file_"))
async def handle_file_request(client, message):
    """Handle file deep links like /start file_xxxxx"""
    file_id_str = message.text.split("_", 1)[1] if "_" in message.text else None
    
    if not file_id_str:
        return
    
    user_id = message.from_user.id
    logger.info(f"File request from {user_id}: {file_id_str}")
    
    # Check verification (admins bypass)
    if user_id not in ADMINS:
        can_access = await verify_db.can_access_file(user_id)
        if not can_access:
            buttons = [[InlineKeyboardButton("🔐 Verify to Access", callback_data="verify_user")]]
            await message.reply(
                "❌ **Access Denied!**\n\nYou need to verify first to access files.",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return
    
    try:
        # Get file from database
        file_data = await db.get_file(ObjectId(file_id_str) if len(file_id_str) == 24 else file_id_str)
        
        if not file_data:
            await message.reply("❌ File not found!")
            return
        
        # Extract file info
        telegram_file_id = file_data.get('file_id')
        mongo_id = str(file_data.get('_id'))
        file_name = file_data.get('file_name', 'Unknown')
        file_size = file_data.get('file_size', 0)
        file_type = file_data.get('file_type', 'document')
        caption = file_data.get('caption', '')
        
        size_str = get_size(file_size)
        
        # ✅ SIMPLE BUTTONS - No streaming (users can download from Telegram)
        buttons = [
            [InlineKeyboardButton("🔞 18+ Videos", url="https://t.me/REAL_TERABOX_PRO_bot")],
            [InlineKeyboardButton("🎬 Join Channel", url="https://t.me/movies_magic_club3")]
        ]
        
        # Build caption
        file_caption = f"**📁 {file_name}**\n\n**📊 Size:** {size_str}\n\n{caption}\n\n**Join:** @movies_magic_club3\n**Owner:** @Siva9789"
        
        # Send actual Telegram file with buttons
        try:
            if file_type == 'video':
                await message.reply_video(
                    telegram_file_id,
                    caption=file_caption,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    parse_mode=enums.ParseMode.MARKDOWN
                )
            elif file_type == 'audio':
                await message.reply_audio(
                    telegram_file_id,
                    caption=file_caption,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    parse_mode=enums.ParseMode.MARKDOWN
                )
            else:
                await message.reply_document(
                    telegram_file_id,
                    caption=file_caption,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    parse_mode=enums.ParseMode.MARKDOWN
                )
            
            logger.info(f"✅ File sent: {file_name} to user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to send file {telegram_file_id}: {e}")
            await message.reply("❌ Error sending file. File may be deleted from Telegram!")
    
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.reply("❌ Error loading file!")


def get_size(size_bytes):
    """Convert bytes to human readable format"""
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = 0
    while size_bytes >= 1024 and i < len(size_name)-1:
        size_bytes /= 1024.
        i += 1
    return f"{size_bytes:.2f} {size_name[i]}"
            
