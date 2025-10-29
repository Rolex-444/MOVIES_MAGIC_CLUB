from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.database import Database
from utils.file_properties import get_size
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)
db = Database()

# Language keywords for filtering
LANGUAGE_KEYWORDS = {
    'Tamil': ['tamil', 'tam', 'தமிழ்'],
    'Telugu': ['telugu', 'tel', 'తెలుగు'],
    'Hindi': ['hindi', 'hin', 'हिन्दी'],
    'Malayalam': ['malayalam', 'mal', 'മലയാളം'],
    'Kannada': ['kannada', 'kan', 'ಕನ್ನಡ'],
    'English': ['english', 'eng']
}

# Quality keywords
QUALITY_KEYWORDS = {
    '2160p': ['2160p', '4k', 'uhd'],
    '1080p': ['1080p', 'fhd', 'fullhd'],
    '720p': ['720p', 'hd'],
    '480p': ['480p', 'sd'],
    '360p': ['360p']
}


def filter_files(files, language=None, quality=None):
    """Filter files by language and quality"""
    if not files:
        return []
    
    filtered = []
    
    for file in files:
        file_name = file.get('file_name', '').lower()
        
        # Language filter
        if language and language != 'All':
            keywords = LANGUAGE_KEYWORDS.get(language, [])
            if not any(kw.lower() in file_name for kw in keywords):
                continue
        
        # Quality filter
        if quality and quality != 'All':
            keywords = QUALITY_KEYWORDS.get(quality, [])
            if not any(kw.lower() in file_name for kw in keywords):
                continue
        
        filtered.append(file)
    
    return filtered


async def get_bot_username(client):
    """Get bot username"""
    try:
        me = await client.get_me()
        return me.username
    except:
        return None


# Language Filter Menu
@Client.on_callback_query(filters.regex(r"^lang#"))
async def language_menu(client, query):
    """Show language selection menu"""
    search = query.data.split("#")[1]
    
    lang_buttons = [
        [InlineKeyboardButton("Tamil", callback_data=f"setlang_Tamil#{search}"),
         InlineKeyboardButton("English", callback_data=f"setlang_English#{search}")],
        [InlineKeyboardButton("Hindi", callback_data=f"setlang_Hindi#{search}"),
         InlineKeyboardButton("Telugu", callback_data=f"setlang_Telugu#{search}")],
        [InlineKeyboardButton("Malayalam", callback_data=f"setlang_Malayalam#{search}"),
         InlineKeyboardButton("Kannada", callback_data=f"setlang_Kannada#{search}")],
        [InlineKeyboardButton("All Languages", callback_data=f"setlang_All#{search}")],
        [InlineKeyboardButton("◀️ Back", callback_data=f"back#{search}")]
    ]
    
    await query.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(lang_buttons)
    )
    await query.answer("Select language")


# Quality Filter Menu
@Client.on_callback_query(filters.regex(r"^qual#"))
async def quality_menu(client, query):
    """Show quality selection menu"""
    search = query.data.split("#")[1]
    
    qual_buttons = [
        [InlineKeyboardButton("2160p 4K", callback_data=f"setqual_2160p#{search}"),
         InlineKeyboardButton("1080p", callback_data=f"setqual_1080p#{search}")],
        [InlineKeyboardButton("720p", callback_data=f"setqual_720p#{search}"),
         InlineKeyboardButton("480p", callback_data=f"setqual_480p#{search}")],
        [InlineKeyboardButton("360p", callback_data=f"setqual_360p#{search}"),
         InlineKeyboardButton("All Quality", callback_data=f"setqual_All#{search}")],
        [InlineKeyboardButton("◀️ Back", callback_data=f"back#{search}")]
    ]
    
    await query.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(qual_buttons)
    )
    await query.answer("Select quality")


# Apply Language Filter
@Client.on_callback_query(filters.regex(r"^setlang_"))
async def set_language_filter(client, query):
    """Apply language filter"""
    data = query.data.split("#")
    language = data[0].replace("setlang_", "")
    search = data[1]
    
    logger.info(f"🎬 Filtering by language: {language}")
    
    # Search files
    files, total = await db.search_files(search)
    
    # Filter by language
    if language != 'All':
        filtered_files = filter_files(files, language=language)
    else:
        filtered_files = files
    
    # Get bot username
    bot_username = await get_bot_username(client)
    
    # Build message
    file_text = f"📁 Found {len(filtered_files)} {language} files for `{search}`\n\n"
    
    for file in filtered_files[:10]:
        try:
            file_id = str(file.get('_id', ''))
            file_name = file.get('file_name', 'Unknown')
            file_size = get_size(file.get('file_size', 0))
            
            deep_link = f"https://t.me/{bot_username}?start=file_{file_id}"
            clickable_text = f'<a href="{deep_link}">📁 {file_size} ▷ {file_name}</a>'
            file_text += f"{clickable_text}\n\n"
        except Exception as e:
            logger.error(f"Error: {e}")
    
    if not filtered_files:
        file_text += "❌ No files found with this filter.\n"
    
    file_text += f"\nJoin: @movies_magic_club3"
    
    # Buttons
    buttons = [
        [InlineKeyboardButton("LANGUAGE", callback_data=f"lang#{search}"),
         InlineKeyboardButton("Quality", callback_data=f"qual#{search}")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    
    try:
        await query.message.edit_text(
            file_text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )
        await query.answer(f"✅ Filtered by {language}", show_alert=False)
    except Exception as e:
        logger.error(f"Error editing message: {e}")
        await query.answer("❌ Error filtering", show_alert=True)


# Apply Quality Filter
@Client.on_callback_query(filters.regex(r"^setqual_"))
async def set_quality_filter(client, query):
    """Apply quality filter"""
    data = query.data.split("#")
    quality = data[0].replace("setqual_", "")
    search = data[1]
    
    logger.info(f"🎬 Filtering by quality: {quality}")
    
    files, total = await db.search_files(search)
    
    if quality != 'All':
        filtered_files = filter_files(files, quality=quality)
    else:
        filtered_files = files
    
    bot_username = await get_bot_username(client)
    
    file_text = f"📁 Found {len(filtered_files)} {quality} files for `{search}`\n\n"
    
    for file in filtered_files[:10]:
        try:
            file_id = str(file.get('_id', ''))
            file_name = file.get('file_name', 'Unknown')
            file_size = get_size(file.get('file_size', 0))
            
            deep_link = f"https://t.me/{bot_username}?start=file_{file_id}"
            clickable_text = f'<a href="{deep_link}">📁 {file_size} ▷ {file_name}</a>'
            file_text += f"{clickable_text}\n\n"
        except Exception as e:
            logger.error(f"Error: {e}")
    
    if not filtered_files:
        file_text += "❌ No files found with this filter.\n"
    
    file_text += f"\nJoin: @movies_magic_club3"
    
    buttons = [
        [InlineKeyboardButton("LANGUAGE", callback_data=f"lang#{search}"),
         InlineKeyboardButton("Quality", callback_data=f"qual#{search}")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    
    try:
        await query.message.edit_text(
            file_text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )
        await query.answer(f"✅ Filtered by {quality}", show_alert=False)
    except Exception as e:
        logger.error(f"Error editing message: {e}")
        await query.answer("❌ Error filtering", show_alert=True)


# Back to Results
@Client.on_callback_query(filters.regex(r"^back#"))
async def back_to_results(client, query):
    """Go back to original results"""
    search = query.data.split("#")[1]
    
    files, total = await db.search_files(search)
    
    bot_username = await get_bot_username(client)
    
    file_text = f"📁 Found {total} files for `{search}`\n\n"
    
    for file in files[:10]:
        try:
            file_id = str(file.get('_id', ''))
            file_name = file.get('file_name', 'Unknown')
            file_size = get_size(file.get('file_size', 0))
            
            deep_link = f"https://t.me/{bot_username}?start=file_{file_id}"
            clickable_text = f'<a href="{deep_link}">📁 {file_size} ▷ {file_name}</a>'
            file_text += f"{clickable_text}\n\n"
        except Exception as e:
            logger.error(f"Error: {e}")
    
    file_text += f"\nJoin: @movies_magic_club3"
    
    buttons = [
        [InlineKeyboardButton("LANGUAGE", callback_data=f"lang#{search}"),
         InlineKeyboardButton("Quality", callback_data=f"qual#{search}")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    
    await query.message.edit_text(
        file_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True
    )
    await query.answer()
    
