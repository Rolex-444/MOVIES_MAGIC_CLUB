from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.database import Database
from database.verify import VerifyDB
from utils.shortlink_api import get_shortlink, generate_verify_token
from utils.file_properties import get_size
from info import *
from config import Config
from bson import ObjectId
import random
import asyncio
import logging
import re

logger = logging.getLogger(__name__)
db = Database()
verify_db = VerifyDB()

# Store user filter preferences temporarily
user_filters = {}


def detect_file_info(filename):
    """Detect language, quality, and season from filename"""
    filename_lower = filename.lower()
    
    # Detect Language
    language = None
    if any(x in filename_lower for x in ['tam', 'tamil']):
        language = 'Tamil'
    elif any(x in filename_lower for x in ['tel', 'telugu']):
        language = 'Telugu'
    elif any(x in filename_lower for x in ['hin', 'hindi']):
        language = 'Hindi'
    elif any(x in filename_lower for x in ['mal', 'malayalam']):
        language = 'Malayalam'
    elif any(x in filename_lower for x in ['kan', 'kannada']):
        language = 'Kannada'
    elif any(x in filename_lower for x in ['eng', 'english']):
        language = 'English'
    
    # Detect Quality
    quality = None
    if '2160p' in filename_lower or '4k' in filename_lower:
        quality = '2160p'
    elif '1080p' in filename_lower:
        quality = '1080p'
    elif '720p' in filename_lower:
        quality = '720p'
    elif '480p' in filename_lower:
        quality = '480p'
    elif '360p' in filename_lower:
        quality = '360p'
    
    # Detect Season
    season = None
    season_match = re.search(r'S(\d+)', filename, re.IGNORECASE)
    if season_match:
        season = f"S{season_match.group(1)}"
    
    return language, quality, season


def filter_files_by_preference(files, user_id):
    """Filter files based on user's language, quality, and season preferences"""
    if user_id not in user_filters:
        return files
    
    prefs = user_filters[user_id]
    filtered = []
    
    for file in files:
        filename = file.get('file_name', '')
        lang, qual, seas = detect_file_info(filename)
        
        # Check language filter
        if 'language' in prefs and prefs['language'] != 'All':
            if lang != prefs['language']:
                continue
        
        # Check quality filter
        if 'quality' in prefs and prefs['quality'] != 'All':
            if qual != prefs['quality']:
                continue
        
        # Check season filter
        if 'season' in prefs and prefs['season'] != 'All':
            if seas != prefs['season']:
                continue
        
        filtered.append(file)
    
    return filtered if filtered else files


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
    
    # Search for files in database
    try:
        result = await db.search_files(search)
        
        # Handle tuple response (files, total)
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
    
    # Build file buttons
    btn = []
    for file in filtered_files[:10]:  # Limit to 10 results
        try:
            file_id = str(file.get('_id', ''))
            file_name = file.get('file_name', 'Unknown')
            
            if file_id:
                btn.append([InlineKeyboardButton(f"📁 {file_name}", callback_data=f"file#{file_id}")])
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            continue
    
    if not btn:
        if SPELL_CHECK:
            await spell_check(client, message, search)
        return
    
    # Add filter buttons (Inline horizontal layout)
    filter_row = [
        InlineKeyboardButton("📂 Languages", callback_data=f"lang_menu#{search}"),
        InlineKeyboardButton("🎬 Qualitys", callback_data=f"qual_menu#{search}"),
        InlineKeyboardButton("📺 Season", callback_data=f"seas_menu#{search}")
    ]
    btn.append(filter_row)
    
    # Add pagination if needed (example: 1/21)
    if total > 10:
        pages = (total // 10) + (1 if total % 10 > 0 else 0)
        btn.append([
            InlineKeyboardButton("📄 PAGES", callback_data="pages"),
            InlineKeyboardButton(f"1/{pages}", callback_data="pages"),
            InlineKeyboardButton("NEXT ⏩", callback_data=f"next_10#{search}")
        ])
    
    btn.append([InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")])
    btn.append([InlineKeyboardButton("❌ Close", callback_data="close")])
    
    # Build caption
    filter_info = ""
    if user_id in user_filters:
        prefs = user_filters[user_id]
        if 'language' in prefs and prefs['language'] != 'All':
            filter_info += f"\n🗣️ Language: {prefs['language']}"
        if 'quality' in prefs and prefs['quality'] != 'All':
            filter_info += f"\n📹 Quality: {prefs['quality']}"
        if 'season' in prefs and prefs['season'] != 'All':
            filter_info += f"\n📺 Season: {prefs['season']}"
    
    caption = f"<b>Found {len(btn)-4} results for:</b> <code>{search}</code>{filter_info}\n\nJoin: @movies_magic_club3"
    
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


# Language Filter Menu
@Client.on_callback_query(filters.regex(r"^lang_menu#"))
async def language_menu(client, query):
    """Show language selection menu"""
    search = query.data.split("#")[1]
    user_id = query.from_user.id
    
    lang_buttons = [
        [InlineKeyboardButton("🇮🇳 Tamil", callback_data=f"setlang_Tamil#{search}"),
         InlineKeyboardButton("🇬🇧 English", callback_data=f"setlang_English#{search}")],
        [InlineKeyboardButton("🇮🇳 Hindi", callback_data=f"setlang_Hindi#{search}"),
         InlineKeyboardButton("🇮🇳 Telugu", callback_data=f"setlang_Telugu#{search}")],
        [InlineKeyboardButton("🇮🇳 Malayalam", callback_data=f"setlang_Malayalam#{search}"),
         InlineKeyboardButton("🇮🇳 Kannada", callback_data=f"setlang_Kannada#{search}")],
        [InlineKeyboardButton("🌐 All Languages", callback_data=f"setlang_All#{search}")],
        [InlineKeyboardButton("◀️ Back", callback_data=f"back#{search}")]
    ]
    
    await query.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(lang_buttons)
    )


# Quality Filter Menu
@Client.on_callback_query(filters.regex(r"^qual_menu#"))
async def quality_menu(client, query):
    """Show quality selection menu"""
    search = query.data.split("#")[1]
    
    qual_buttons = [
        [InlineKeyboardButton("4K 2160p", callback_data=f"setqual_2160p#{search}"),
         InlineKeyboardButton("📺 1080p", callback_data=f"setqual_1080p#{search}")],
        [InlineKeyboardButton("🎬 720p", callback_data=f"setqual_720p#{search}"),
         InlineKeyboardButton("📱 480p", callback_data=f"setqual_480p#{search}")],
        [InlineKeyboardButton("📲 360p", callback_data=f"setqual_360p#{search}"),
         InlineKeyboardButton("🌐 All Quality", callback_data=f"setqual_All#{search}")],
        [InlineKeyboardButton("◀️ Back", callback_data=f"back#{search}")]
    ]
    
    await query.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(qual_buttons)
    )


# Season Filter Menu
@Client.on_callback_query(filters.regex(r"^seas_menu#"))
async def season_menu(client, query):
    """Show season selection menu"""
    search = query.data.split("#")[1]
    
    seas_buttons = [
        [InlineKeyboardButton("S1", callback_data=f"setseas_S1#{search}"),
         InlineKeyboardButton("S2", callback_data=f"setseas_S2#{search}"),
         InlineKeyboardButton("S3", callback_data=f"setseas_S3#{search}")],
        [InlineKeyboardButton("S4", callback_data=f"setseas_S4#{search}"),
         InlineKeyboardButton("S5", callback_data=f"setseas_S5#{search}"),
         InlineKeyboardButton("S6", callback_data=f"setseas_S6#{search}")],
        [InlineKeyboardButton("🌐 All Seasons", callback_data=f"setseas_All#{search}")],
        [InlineKeyboardButton("◀️ Back", callback_data=f"back#{search}")]
    ]
    
    await query.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(seas_buttons)
    )


# Set Language Filter
@Client.on_callback_query(filters.regex(r"^setlang_"))
async def set_language(client, query):
    """Set user's language preference"""
    data_parts = query.data.split("#")
    language = data_parts[0].replace("setlang_", "")
    search = data_parts[1]
    user_id = query.from_user.id
    
    # Store preference
    if user_id not in user_filters:
        user_filters[user_id] = {}
    user_filters[user_id]['language'] = language
    
    await query.answer(f"✅ Language set to {language}", show_alert=False)
    
    # Refresh search results with filter
    await refresh_results(client, query.message, search, user_id)


# Set Quality Filter
@Client.on_callback_query(filters.regex(r"^setqual_"))
async def set_quality(client, query):
    """Set user's quality preference"""
    data_parts = query.data.split("#")
    quality = data_parts[0].replace("setqual_", "")
    search = data_parts[1]
    user_id = query.from_user.id
    
    if user_id not in user_filters:
        user_filters[user_id] = {}
    user_filters[user_id]['quality'] = quality
    
    await query.answer(f"✅ Quality set to {quality}", show_alert=False)
    
    await refresh_results(client, query.message, search, user_id)


# Set Season Filter
@Client.on_callback_query(filters.regex(r"^setseas_"))
async def set_season(client, query):
    """Set user's season preference"""
    data_parts = query.data.split("#")
    season = data_parts[0].replace("setseas_", "")
    search = data_parts[1]
    user_id = query.from_user.id
    
    if user_id not in user_filters:
        user_filters[user_id] = {}
    user_filters[user_id]['season'] = season
    
    await query.answer(f"✅ Season set to {season}", show_alert=False)
    
    await refresh_results(client, query.message, search, user_id)


async def refresh_results(client, message, search, user_id):
    """Refresh search results with applied filters"""
    try:
        result = await db.search_files(search)
        
        if isinstance(result, tuple):
            files, total = result
        else:
            files = result
        
        filtered_files = filter_files_by_preference(files, user_id)
        
        btn = []
        for file in filtered_files[:10]:
            file_id = str(file.get('_id', ''))
            file_name = file.get('file_name', 'Unknown')
            if file_id:
                btn.append([InlineKeyboardButton(f"📁 {file_name}", callback_data=f"file#{file_id}")])
        
        if not btn:
            btn.append([InlineKeyboardButton("❌ No files match your filters", callback_data="none")])
        
        # Add filter buttons
        filter_row = [
            InlineKeyboardButton("📂 Languages", callback_data=f"lang_menu#{search}"),
            InlineKeyboardButton("🎬 Qualitys", callback_data=f"qual_menu#{search}"),
            InlineKeyboardButton("📺 Season", callback_data=f"seas_menu#{search}")
        ]
        btn.append(filter_row)
        
        btn.append([InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")])
        btn.append([InlineKeyboardButton("❌ Close", callback_data="close")])
        
        # Build caption with filter info
        filter_info = ""
        if user_id in user_filters:
            prefs = user_filters[user_id]
            if 'language' in prefs and prefs['language'] != 'All':
                filter_info += f"\n🗣️ Language: {prefs['language']}"
            if 'quality' in prefs and prefs['quality'] != 'All':
                filter_info += f"\n📹 Quality: {prefs['quality']}"
            if 'season' in prefs and prefs['season'] != 'All':
                filter_info += f"\n📺 Season: {prefs['season']}"
        
        caption = f"<b>Found {len(filtered_files)} results for:</b> <code>{search}</code>{filter_info}\n\nJoin: @movies_magic_club3"
        
        await message.edit_caption(
            caption=caption,
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Refresh error: {e}")


@Client.on_callback_query(filters.regex(r"^back#"))
async def back_to_results(client, query):
    """Go back to search results"""
    search = query.data.split("#")[1]
    user_id = query.from_user.id
    await refresh_results(client, query.message, search, user_id)


@Client.on_callback_query(filters.regex(r"^file#"))
async def send_file(client, query):
    """Send file with verification check"""
    user_id = query.from_user.id
    file_id = query.data.split("#")[1]
    
    logger.info(f"File button clicked by user {user_id}, file_id: {file_id}")
    
    # Check if user is admin (admins bypass everything)
    if user_id not in ADMINS:
        # Check if user can access file (verified or under free limit)
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
    try:
        # Convert string ID to ObjectId for MongoDB
        if len(file_id) == 24:  # MongoDB ObjectId length
            mongo_id = ObjectId(file_id)
        else:
            mongo_id = file_id
        
        file_data = await db.get_file(mongo_id)
        logger.info(f"File data retrieved: {file_data is not None}")
        
    except Exception as e:
        logger.error(f"Error getting file {file_id}: {e}")
        file_data = None
    
    if not file_data:
        await query.answer("❌ File not found in database!", show_alert=True)
        logger.error(f"File not found for ID: {file_id}")
        return
    
    # Build caption
    try:
        caption = CUSTOM_FILE_CAPTION if CUSTOM_FILE_CAPTION else Config.FILE_CAPTION
        caption = caption.format(
            file_name=file_data.get('file_name', 'Unknown'),
            file_size=get_size(file_data.get('file_size', 0)),
            caption=file_data.get('caption', '')
        )
    except Exception as e:
        logger.error(f"Caption format error: {e}")
        caption = f"<b>{file_data.get('file_name', 'File')}</b>\n\nJoin: @movies_magic_club3"
    
    # Build buttons
    file_buttons = [
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
        logger.info(f"File sent successfully to user {user_id}")
        
        # Auto delete if enabled
        if AUTO_DELETE:
            await asyncio.sleep(AUTO_DELETE_TIME)
            try:
                await msg.delete()
            except:
                pass
                
    except Exception as e:
        logger.error(f"Send file error: {e}")
        await query.answer(f"❌ Error: Start the bot in PM first!", show_alert=True)


@Client.on_callback_query(filters.regex("^close$"))
async def close_callback(client, query):
    """Close button handler"""
    try:
        await query.message.delete()
        await query.answer("Closed!", show_alert=False)
    except:
        await query.answer("Already closed!", show_alert=False)
                
