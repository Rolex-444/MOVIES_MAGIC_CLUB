from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.database import Database
from database.verify import VerifyDB
from utils.shortlink_api import get_shortlink, generate_verify_token
from utils.file_properties import get_size
from utils.file_detector import filter_files_by_preference, get_filter_info
from info import *
from config import Config
from bson import ObjectId
import random
import asyncio
import logging

logger = logging.getLogger(__name__)
db = Database()
verify_db = VerifyDB()


async def spell_check(client, message, search):
    """Spell check function for incorrect movie names"""
    try:
        await message.reply(
            f"❌ <b>No results found for:</b> <code>{search}</code>\n\n"
            "💡 <b>Suggestions:</b>\n"
            "• Check your spelling\n"
            "• Try different keywords\n"
            "• Use movie name only (without year)\n\n"
            "Join: @movies_magic_club3",
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Spell check error: {e}")


@Client.on_message(filters.text & filters.group)
async def auto_filter(client, message):
    """Auto filter for group search queries"""
    if message.text.startswith('/'):
        return
    
    search = message.text
    user_id = message.from_user.id
    
    # Get bot username for deep links
    me = await client.get_me()
    bot_username = me.username
    
    # Search for files in database
    try:
        result = await db.search_files(search)
        
        if isinstance(result, tuple):
            files, total = result
        else:
            files = result
            total = len(files) if files else 0
            
        logger.info(f"Found {total} files for search: {search}")
        
    except Exception as e:
        logger.error(f"Database search error: {e}")
        files = []
        total = 0
    
    if not files:
        if SPELL_CHECK:
            await spell_check(client, message, search)
        return
    
    # Apply filters if user has set preferences
    filtered_files = filter_files_by_preference(files, user_id)
    
    if not filtered_files:
        await message.reply(
            f"<b>No files match your filters for:</b> <code>{search}</code>\n\nTry selecting 'All' in filters.",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    # Build text with clickable links (HTML <a> tags)
    file_text = f"<b>📂 HERE I FOUND FOR YOUR SEARCH</b> <code>{search}</code>\n\n"
    
    for idx, file in enumerate(filtered_files[:10], 1):
        try:
            file_id = str(file.get('_id', ''))
            file_name = file.get('file_name', 'Unknown')
            file_size = get_size(file.get('file_size', 0))
            
            # Create deep link: https://t.me/BOT_USERNAME?start=file_FILE_ID
            deep_link = f"https://t.me/{bot_username}?start=file_{file_id}"
            
            # Format as clickable HTML link: <a href="deep_link">📁 SIZE ▷ FILENAME</a>
            clickable_text = f'<a href="{deep_link}">📁 {file_size} ▷ {file_name}</a>'
            
            file_text += f"{clickable_text}\n\n"
            
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            continue
    
    # Add filter buttons ONLY (no file buttons)
    btn = []
    filter_row = [
        InlineKeyboardButton("LANGUAGES", callback_data=f"lang#{search}"),
        InlineKeyboardButton("Qualitys", callback_data=f"qual#{search}"),
        InlineKeyboardButton("Season", callback_data=f"seas#{search}")
    ]
    btn.append(filter_row)
    
    # Add pagination if needed
    if len(filtered_files) > 10:
        pages = (len(filtered_files) // 10) + (1 if len(filtered_files) % 10 > 0 else 0)
        nav_row = [
            InlineKeyboardButton("📄 PAGES", callback_data="pages_info"),
            InlineKeyboardButton(f"1/{pages}", callback_data="pages_info"),
            InlineKeyboardButton("NEXT ⏩", callback_data=f"next_10#{search}")
        ]
        btn.append(nav_row)
    
    btn.append([InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")])
    btn.append([InlineKeyboardButton("❌ Close", callback_data="close")])
    
    # Build caption with filter info
    filter_info = get_filter_info(user_id)
    file_text += filter_info + "\n\nJoin: @movies_magic_club3"
    
    try:
        await message.reply(
            file_text,
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Send message error: {e}")


# Handle deep link clicks from /start command
@Client.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    """Handle /start command and deep links"""
    user_id = message.from_user.id
    
    # Check if it's a deep link (e.g., /start file_FILE_ID)
    if len(message.command) > 1:
        parameter = message.command[1]
        
        # Handle file deep link
        if parameter.startswith("file_"):
            file_id = parameter.replace("file_", "")
            logger.info(f"Deep link file access: user {user_id}, file_id {file_id}")
            
            # Use the existing send_file logic
            await send_file_by_deeplink(client, message, file_id)
            return
    
    # Regular /start message (your existing start message)
    buttons = [
        [InlineKeyboardButton("🆘 Help", callback_data="help"),
         InlineKeyboardButton("ℹ️ About", callback_data="about")],
        [InlineKeyboardButton("🔐 Verify", callback_data="verify_user"),
         InlineKeyboardButton("👑 Premium", callback_data="premium")],
        [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")],
        [InlineKeyboardButton("🎬 Join Channel", url="https://t.me/movies_magic_club3")]
    ]
    
    await message.reply(
        Config.START_TXT.format(message.from_user.first_name),
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )


async def send_file_by_deeplink(client, message, file_id):
    """Send file when accessed via deep link"""
    user_id = message.from_user.id
    
    # Check if user is admin (admins bypass everything)
    if user_id not in ADMINS:
        # Check if user can access file (verified or under free limit)
        can_access = await verify_db.can_access_file(user_id)
        
        if not can_access:
            # User needs to verify
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
            
            await message.reply(
                Config.VERIFY_TXT,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True
            )
            return
        
        # Increment file attempts for non-verified users
        if not await verify_db.is_verified(user_id):
            await verify_db.increment_file_attempts(user_id)
    
    # Get file data from database
    try:
        if len(file_id) == 24:
            mongo_id = ObjectId(file_id)
        else:
            mongo_id = file_id
        
        file_data = await db.get_file(mongo_id)
        
    except Exception as e:
        logger.error(f"Error getting file {file_id}: {e}")
        file_data = None
    
    if not file_data:
        await message.reply("❌ <b>File not found!</b>", parse_mode=enums.ParseMode.HTML)
        return
    
    # Build caption
    try:
        caption = CUSTOM_FILE_CAPTION if CUSTOM_FILE_CAPTION else Config.FILE_CAPTION
        caption = caption.format(
            file_name=file_data.get('file_name', 'Unknown'),
            file_size=get_size(file_data.get('file_size', 0)),
            caption=file_data.get('caption', '')
        )
    except:
        caption = f"<b>{file_data.get('file_name', 'File')}</b>\n\nJoin: @movies_magic_club3"
    
    # Build buttons
    file_buttons = [
        [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")],
        [InlineKeyboardButton("🎬 Join Channel", url="https://t.me/movies_magic_club3")]
    ]
    
    try:
        # Send file to user
        msg = await client.send_cached_media(
            chat_id=user_id,
            file_id=file_data.get('file_id'),
            caption=caption,
            reply_markup=InlineKeyboardMarkup(file_buttons),
            parse_mode=enums.ParseMode.HTML,
            protect_content=PROTECT_CONTENT
        )
        
        # Auto delete if enabled
        if AUTO_DELETE:
            await asyncio.sleep(AUTO_DELETE_TIME)
            try:
                await msg.delete()
            except:
                pass
                
    except Exception as e:
        logger.error(f"Send file error: {e}")
        await message.reply(f"❌ <b>Error:</b> {e}", parse_mode=enums.ParseMode.HTML)


@Client.on_callback_query(filters.regex(r"^file#"))
async def send_file(client, query):
    """Send file with verification check (callback from buttons)"""
    user_id = query.from_user.id
    file_id = query.data.split("#")[1]
    
    # Same logic as send_file_by_deeplink but for callback queries
    # (Keep your existing send_file function here for backward compatibility)
    pass


@Client.on_callback_query(filters.regex("^close$"))
async def close_callback(client, query):
    """Close button handler"""
    try:
        await query.message.delete()
        await query.answer("Closed!", show_alert=False)
    except:
        await query.answer("Already closed!", show_alert=False)
        
