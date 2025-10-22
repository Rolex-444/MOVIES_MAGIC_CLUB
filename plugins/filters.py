from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bson import ObjectId
from info import *
from utils import get_size, get_shortlink, generate_verify_token
from database import db, verify_db, filter_db
import logging

logger = logging.getLogger(__name__)

# Global dict for user filters
user_filters = {}

def get_filter_info(user_id):
    """Get current filter settings"""
    if user_id not in user_filters:
        return "📊 Filter: All | All | All"
    
    filters_data = user_filters[user_id]
    lang = filters_data.get('language', 'All')
    qual = filters_data.get('quality', 'All')
    seas = filters_data.get('season', 'All')
    return f"📊 Filter: {lang} | {qual} | {seas}"

def apply_user_filters(files, user_id):
    """Apply user's selected filters"""
    if user_id not in user_filters:
        return files
    
    filters_data = user_filters[user_id]
    filtered = files
    
    # Filter by language
    if filters_data.get('language') and filters_data['language'] != 'All':
        filtered = [f for f in filtered if filters_data['language'].lower() in f.get('file_name', '').lower()]
    
    # Filter by quality
    if filters_data.get('quality') and filters_data['quality'] != 'All':
        filtered = [f for f in filtered if filters_data['quality'].lower() in f.get('file_name', '').lower()]
    
    # Filter by season
    if filters_data.get('season') and filters_data['season'] != 'All':
        filtered = [f for f in filtered if filters_data['season'].lower() in f.get('file_name', '').lower()]
    
    return filtered

@Client.on_message(filters.text & filters.group)
async def auto_filter(client, message):
    """Auto-filter for movies in groups"""
    search = message.text
    user_id = message.from_user.id
    
    # Get bot username for deep links
    me = await client.get_me()
    bot_username = me.username
    
    # Search files in database
    files = await db.get_search_results(search)
    
    if not files:
        return
    
    # Apply user filters
    filtered_files = apply_user_filters(files, user_id)
    
    if not filtered_files:
        await message.reply(
            f"<b>🔍 Found: <code>{search}</code></b>\n\n"
            f"💡 <b>No results for <code>{search}</code></b>\n\nTry selecting 'All' in filters.",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    # Build text with clickable links (HTML tags)
    file_text = f"<b>🔍 Found: <code>{search}</code></b>\n\n"
    
    for idx, file in enumerate(filtered_files[:10], 1):
        try:
            file_id = str(file.get('_id', ''))
            file_name = file.get('file_name', 'Unknown')
            file_size = get_size(file.get('file_size', 0))
            
            # Create deep link: https://t.me/BOT_USERNAME?start=file_FILE_ID
            deep_link = f"https://t.me/{bot_username}?start=file_{file_id}"
            
            # Format as clickable HTML link: 📁 SIZE ▷ FILENAME
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
        await message.reply("❌ File not found!")
        return
    
    # Extract file info
    file_name = file_data.get('file_name', 'Unknown')
    file_size = get_size(file_data.get('file_size', 0))
    caption_text = file_data.get('caption', '')
    file_link = file_data.get('file_link', '')  # Terabox link
    
    # === NEW: STREAMING BUTTONS ===
    # Add Fast Download and Watch Online buttons
    buttons = [
        [InlineKeyboardButton("⚡ Fast Download", callback_data=f"dl:{file_link}")],
        [InlineKeyboardButton("🎬 Watch Online", callback_data=f"st:{file_link}:{file_name}")],
        [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")]
    ]
    
    # Send file details with streaming buttons
    caption = f"📁 **{file_name}**\n\n📊 Size: {file_size}\n\n{caption_text}\n\n{file_link}\n\nJoin: @movies_magic_club3\nOwner: @Siva9789"
    
    await message.reply(
        caption,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.MARKDOWN
    )
    
