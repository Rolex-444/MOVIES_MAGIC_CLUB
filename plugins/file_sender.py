from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.database import Database
from database.verify import VerifyDB
from bson import ObjectId
from info import ADMINS, SHORTLINK_URL, SHORTLINK_API, VERIFY_TUTORIAL
from utils.shortlink_api import get_shortlink, generate_verify_token
from config import Config
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
    logger.info(f"📥 File request from {user_id}: {file_id_str}")
    
    # Check verification (admins bypass all checks)
    if user_id not in ADMINS:
        # Check if user can access files
        can_access = await verify_db.can_access_file(user_id)
        logger.info(f"🔐 User {user_id} access check: {can_access}")
        
        if not can_access:
            # User needs to verify - Generate shortlink
            token = generate_verify_token()
            await verify_db.set_verify_token(user_id, token, 600)
            
            me = await client.get_me()
            verify_url = f"https://t.me/{me.username}?start=verify_{token}"
            short_url = get_shortlink(verify_url, SHORTLINK_URL, SHORTLINK_API)
            
            buttons = [
                [InlineKeyboardButton("🔐 Verify Now", url=short_url)],
                [InlineKeyboardButton("📚 How to Verify?", url=VERIFY_TUTORIAL)],
                [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")]
            ]
            
            logger.info(f"⚠️ User {user_id} needs verification - showing shortlink")
            
            await message.reply(
                Config.VERIFY_TXT,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True
            )
            return
        
        # Increment file attempts for non-verified users (free users)
        if not await verify_db.is_verified(user_id):
            await verify_db.increment_file_attempts(user_id)
            
            # Get current attempts for logging
            user = await verify_db.get_user(user_id)
            attempts = user.get("file_attempts", 0) if user else 0
            logger.info(f"📊 User {user_id} file attempts: {attempts}/5")
    
    # Get file from database
    try:
        # Convert to ObjectId if it's a valid MongoDB ID
        if len(file_id_str) == 24:
            file_data = await db.get_file(ObjectId(file_id_str))
        else:
            file_data = await db.get_file(file_id_str)
        
        if not file_data:
            logger.error(f"❌ File not found: {file_id_str}")
            await message.reply(
                "❌ <b>File not found!</b>\n\nThis file may have been deleted.",
                parse_mode=enums.ParseMode.HTML
            )
            return
        
        # Extract file information
        telegram_file_id = file_data.get('file_id')
        file_name = file_data.get('file_name', 'Unknown')
        file_size = file_data.get('file_size', 0)
        file_type = file_data.get('file_type', 'document')
        caption = file_data.get('caption', '')
        
        # Format file size
        size_str = get_size(file_size)
        
        # Build caption
        file_caption = f"**📁 {file_name}**\n\n**📊 Size:** {size_str}\n\n{caption}\n\n**Join:** @movies_magic_club3\n**Owner:** @Siva9789"
        
        # Build buttons
        buttons = [
            [InlineKeyboardButton("🔞 18+ Videos", url="https://t.me/REAL_TERABOX_PRO_bot")],
            [InlineKeyboardButton("🎬 Join Channel", url="https://t.me/movies_magic_club3")]
        ]
        
        # Send file based on type
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
            logger.error(f"❌ Failed to send file {telegram_file_id}: {e}")
            await message.reply(
                "❌ <b>Error sending file!</b>\n\nFile may be deleted from Telegram servers.",
                parse_mode=enums.ParseMode.HTML
            )
            
    except Exception as e:
        logger.error(f"❌ Error processing file request: {e}")
        await message.reply(
            "❌ <b>Error loading file!</b>\n\nPlease try again later.",
            parse_mode=enums.ParseMode.HTML
        )


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
            
