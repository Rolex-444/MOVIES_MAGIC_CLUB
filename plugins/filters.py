from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.database import Database
from database.verify import VerifyDB
from utils.shortlink_api import get_shortlink, generate_verify_token
from utils.file_properties import get_size
from info import *
from config import Config
import random
import asyncio
import logging

logger = logging.getLogger(__name__)
db = Database()
verify_db = VerifyDB()


async def get_imdb_info(query):
    """Get IMDB info for movie - Returns None if IMDB not configured"""
    try:
        # IMDB integration can be added here later
        # For now, return None to skip IMDB
        return None
    except:
        return None


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
    
    # Search for files in database
    try:
        files = await db.search_files(search)
    except Exception as e:
        logger.error(f"Database search error: {e}")
        files = []
    
    if not files:
        if SPELL_CHECK:
            await spell_check(client, message, search)
        return
    
    # Build file buttons
    btn = []
    for file in files[:10]:  # Limit to 10 results
        file_id = str(file.get('_id'))
        file_name = file.get('file_name', 'Unknown')
        
        btn.append([InlineKeyboardButton(f"📁 {file_name}", callback_data=f"file#{file_id}")])
    
    btn.append([InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")])
    btn.append([InlineKeyboardButton("❌ Close", callback_data="close")])
    
    # Build caption (IMDB disabled for now)
    caption = f"<b>Found {len(files)} results for:</b> <code>{search}</code>\n\nJoin: @movies_magic_club3"
    
    try:
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=caption,
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )
    except Exception:
        await message.reply(
            caption,
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.HTML
        )


@Client.on_callback_query(filters.regex(r"^file#"))
async def send_file(client, query):
    """Send file with verification check"""
    user_id = query.from_user.id
    file_id = query.data.split("#")[1]
    
    # Check if user is admin (admins bypass everything)
    if user_id not in ADMINS:
        # Check if user can access file (verified or under free limit)
        can_access = await verify_db.can_access_file(user_id)
        
        if not can_access:
            # User needs to verify
            token = generate_verify_token()
            await verify_db.set_verify_token(user_id, token, 600)  # Token valid for 10 mins
            
            # Get bot username
            me = await client.get_me()
            verify_url = f"https://t.me/{me.username}?start=verify_{token}"
            short_url = get_shortlink(verify_url, SHORTLINK_URL, SHORTLINK_API)
            
            buttons = [
                [InlineKeyboardButton("🔐 Verify Now", url=short_url)],
                [InlineKeyboardButton("📚 How to Verify?", url=VERIFY_TUTORIAL)],
                [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")]
            ]
            
            await query.answer("⚠️ Verification required!", show_alert=True)
            await query.message.reply(
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
    file_data = await db.get_file(file_id)
    if not file_data:
        await query.answer("❌ File not found in database!", show_alert=True)
        return
    
    # Build caption
    caption = CUSTOM_FILE_CAPTION if CUSTOM_FILE_CAPTION else Config.FILE_CAPTION
    caption = caption.format(
        file_name=file_data.get('file_name', 'Unknown'),
        file_size=get_size(file_data.get('file_size', 0)),
        caption=file_data.get('caption', '')
    )
    
    # Build buttons
    file_buttons = [
        [InlineKeyboardButton("🎬 Stream", callback_data=f"stream#{file_id}"),
         InlineKeyboardButton("⚡ Fast Download", callback_data=f"fast#{file_id}")],
        [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")],
        [InlineKeyboardButton("🎬 Join Channel", url="https://t.me/movies_magic_club3")]
    ]
    
    try:
        # Send file to user's PM
        msg = await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_data.get('file_id'),
            caption=caption,
            reply_markup=InlineKeyboardMarkup(file_buttons),
            parse_mode=enums.ParseMode.HTML,
            protect_content=PROTECT_CONTENT
        )
        
        await query.answer("✅ File sent to PM!", show_alert=False)
        
        # Auto delete if enabled
        if AUTO_DELETE:
            await asyncio.sleep(AUTO_DELETE_TIME)
            try:
                await msg.delete()
            except:
                pass
                
    except Exception as e:
        await query.answer(f"❌ Error: {e}", show_alert=True)


async def send_file_by_id(client, message, file_id):
    """Send file by ID (used in start command deep links)"""
    user_id = message.from_user.id
    
    # Check if user is admin
    if user_id not in ADMINS:
        # Check if user can access file
        can_access = await verify_db.can_access_file(user_id)
        
        if not can_access:
            # User needs to verify
            token = generate_verify_token()
            await verify_db.set_verify_token(user_id, token, 600)
            
            # Get bot username
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
    
    # Get file data
    file_data = await db.get_file(file_id)
    if not file_data:
        await message.reply("❌ <b>File not found!</b>", parse_mode=enums.ParseMode.HTML)
        return
    
    # Build caption
    caption = CUSTOM_FILE_CAPTION if CUSTOM_FILE_CAPTION else Config.FILE_CAPTION
    caption = caption.format(
        file_name=file_data.get('file_name', 'Unknown'),
        file_size=get_size(file_data.get('file_size', 0)),
        caption=file_data.get('caption', '')
    )
    
    # Build buttons
    file_buttons = [
        [InlineKeyboardButton("🎬 Stream", callback_data=f"stream#{file_id}"),
         InlineKeyboardButton("⚡ Fast Download", callback_data=f"fast#{file_id}")],
        [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")],
        [InlineKeyboardButton("🎬 Join Channel", url="https://t.me/movies_magic_club3")]
    ]
    
    try:
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
        await message.reply(f"❌ <b>Error:</b> {e}", parse_mode=enums.ParseMode.HTML)


@Client.on_callback_query(filters.regex("^close$"))
async def close_callback(client, query):
    """Close button handler"""
    await query.message.delete()
    await query.answer("Closed!", show_alert=False)


@Client.on_callback_query(filters.regex(r"^next_"))
async def next_page(client, query):
    """Handle pagination - next page"""
    _, offset = query.data.split("_")
    search = query.message.caption.split("for:")[1].split("\n")[0].strip() if "for:" in query.message.caption else ""
    
    try:
        files = await db.search_files(search, offset=int(offset))
    except:
        files = []
    
    if not files:
        await query.answer("No more results!", show_alert=True)
        return
    
    btn = []
    for file in files[:10]:
        file_id = str(file.get('_id'))
        file_name = file.get('file_name', 'Unknown')
        btn.append([InlineKeyboardButton(f"📁 {file_name}", callback_data=f"file#{file_id}")])
    
    btn.append([InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")])
    btn.append([InlineKeyboardButton("❌ Close", callback_data="close")])
    
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
        await query.answer()
    except Exception as e:
        await query.answer(f"Error: {e}", show_alert=True)
        
