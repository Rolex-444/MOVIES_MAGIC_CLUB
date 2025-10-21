from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.database import Database
from utils.file_detector import set_user_filter, filter_files_by_preference, get_filter_info
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)
db = Database()


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
    await query.answer()


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
         InlineKeyboardButton("All Qualitys", callback_data=f"setqual_All#{search}")],
        [InlineKeyboardButton("◀️ Back", callback_data=f"back#{search}")]
    ]
    
    await query.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(qual_buttons)
    )
    await query.answer()


# Season Filter Menu
@Client.on_callback_query(filters.regex(r"^seas#"))
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
        [InlineKeyboardButton("All Seasons", callback_data=f"setseas_All#{search}")],
        [InlineKeyboardButton("◀️ Back", callback_data=f"back#{search}")]
    ]
    
    await query.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(seas_buttons)
    )
    await query.answer()


# Set Language Filter
@Client.on_callback_query(filters.regex(r"^setlang_"))
async def set_language(client, query):
    """Set user's language preference"""
    data_parts = query.data.split("#")
    language = data_parts[0].replace("setlang_", "")
    search = data_parts[1]
    user_id = query.from_user.id
    
    set_user_filter(user_id, 'language', language)
    
    await query.answer(f"✅ Language: {language}", show_alert=False)
    await refresh_results(client, query.message, search, user_id)


# Set Quality Filter
@Client.on_callback_query(filters.regex(r"^setqual_"))
async def set_quality(client, query):
    """Set user's quality preference"""
    data_parts = query.data.split("#")
    quality = data_parts[0].replace("setqual_", "")
    search = data_parts[1]
    user_id = query.from_user.id
    
    set_user_filter(user_id, 'quality', quality)
    
    await query.answer(f"✅ Quality: {quality}", show_alert=False)
    await refresh_results(client, query.message, search, user_id)


# Set Season Filter
@Client.on_callback_query(filters.regex(r"^setseas_"))
async def set_season(client, query):
    """Set user's season preference"""
    data_parts = query.data.split("#")
    season = data_parts[0].replace("setseas_", "")
    search = data_parts[1]
    user_id = query.from_user.id
    
    set_user_filter(user_id, 'season', season)
    
    await query.answer(f"✅ Season: {season}", show_alert=False)
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
            btn.append([InlineKeyboardButton("❌ No files match filters", callback_data="none")])
        
        # Add filter buttons (single row)
        filter_row = [
            InlineKeyboardButton("LANGUAGES", callback_data=f"lang#{search}"),
            InlineKeyboardButton("Qualitys", callback_data=f"qual#{search}"),
            InlineKeyboardButton("Season", callback_data=f"seas#{search}")
        ]
        btn.append(filter_row)
        
        btn.append([InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")])
        btn.append([InlineKeyboardButton("❌ Close", callback_data="close")])
        
        filter_info = get_filter_info(user_id)
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
