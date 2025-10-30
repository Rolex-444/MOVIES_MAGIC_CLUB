from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.database import Database
from utils.file_properties import get_size
import logging
import re

logger = logging.getLogger(__name__)
db = Database()

# Language keywords for filtering
LANGUAGE_KEYWORDS = {
    'Tamil': ['tamil', 'tam', '.tam.', '[tam]', 'தமிழ்', 'tmv', 'tn'],
    'Telugu': ['telugu', 'tel', '.tel.', '[tel]', 'తెలుగు', 'tlu'],
    'Hindi': ['hindi', 'hin', '.hin.', '[hin]', 'हिन्दी', 'hnd'],
    'Malayalam': ['malayalam', 'mal', '.mal.', '[mal]', 'മലയാളം', 'mlm'],
    'Kannada': ['kannada', 'kan', '.kan.', '[kan]', 'ಕನ್ನಡ', 'knd'],
    'English': ['english', 'eng', '.eng.', '[eng]', 'dual audio']
}

# Quality keywords
QUALITY_KEYWORDS = {
    '2160p': ['2160p', '4k', 'uhd', '2160'],
    '1080p': ['1080p', 'fhd', 'fullhd', '1080'],
    '720p': ['720p', 'hd', '720'],
    '480p': ['480p', 'sd', '480'],
    '360p': ['360p', '360']
}


def filter_files(files, language=None, quality=None, season=None, episode=None):
    """Filter files by language, quality, season and episode"""
    if not files:
        return []
    
    filtered = []
    
    for file in files:
        original_caption = file.get('caption', '').lower()
        file_name = file.get('file_name', '').lower()
        search_text = f"{original_caption} {file_name}"
        
        match = True
        
        # Language filter
        if language and language != 'All':
            keywords = LANGUAGE_KEYWORDS.get(language, [])
            lang_found = any(kw.lower() in search_text for kw in keywords)
            if not lang_found:
                match = False
        
        # Quality filter
        if quality and quality != 'All':
            keywords = QUALITY_KEYWORDS.get(quality, [])
            qual_found = any(kw.lower() in search_text for kw in keywords)
            if not qual_found:
                match = False
        
        # Season filter (e.g., S01, S02, Season 1)
        if season and season != 'All':
            season_patterns = [
                f's{season}',  # S01
                f's0{season}',  # S01
                f'season {season}',  # Season 1
                f'season{season}',  # Season1
            ]
            season_found = any(pattern in search_text for pattern in season_patterns)
            if not season_found:
                match = False
        
        # Episode filter (e.g., E01, E02, Episode 1)
        if episode and episode != 'All':
            episode_patterns = [
                f'e{episode}',  # E01
                f'e0{episode}',  # E01
                f'episode {episode}',  # Episode 1
                f'episode{episode}',  # Episode1
                f'ep{episode}',  # Ep01
            ]
            episode_found = any(pattern in search_text for pattern in episode_patterns)
            if not episode_found:
                match = False
        
        if match:
            filtered.append(file)
    
    logger.info(f"🎬 Filtered: {len(filtered)}/{len(files)} files")
    return filtered


async def get_bot_username(client):
    """Get bot username"""
    try:
        me = await client.get_me()
        return me.username
    except:
        return None


def clean_caption(caption):
    """Clean caption for display"""
    if not caption:
        return caption
    caption = re.sub(r'@\w+', '', caption)
    caption = re.sub(r'(https?://)?(t\.me|telegram\.me)/\S+', '', caption)
    caption = re.sub(r'\s+', ' ', caption)
    return caption.strip()


# Language Filter Menu
@Client.on_callback_query(filters.regex(r"^lang#"))
async def language_menu(client, query):
    """Show language selection menu"""
    search = query.data.split("#")[1]
    
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
    await query.answer("🎭 Select language")


# Quality Filter Menu
@Client.on_callback_query(filters.regex(r"^qual#"))
async def quality_menu(client, query):
    """Show quality selection menu"""
    search = query.data.split("#")[1]
    
    qual_buttons = [
        [InlineKeyboardButton("🎬 2160p 4K", callback_data=f"setqual_2160p#{search}"),
         InlineKeyboardButton("📺 1080p", callback_data=f"setqual_1080p#{search}")],
        [InlineKeyboardButton("📺 720p", callback_data=f"setqual_720p#{search}"),
         InlineKeyboardButton("📱 480p", callback_data=f"setqual_480p#{search}")],
        [InlineKeyboardButton("📱 360p", callback_data=f"setqual_360p#{search}"),
         InlineKeyboardButton("🌐 All Quality", callback_data=f"setqual_All#{search}")],
        [InlineKeyboardButton("◀️ Back", callback_data=f"back#{search}")]
    ]
    
    await query.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(qual_buttons)
    )
    await query.answer("🎬 Select quality")


# Season Filter Menu
@Client.on_callback_query(filters.regex(r"^season#"))
async def season_menu(client, query):
    """Show season selection menu"""
    search = query.data.split("#")[1]
    
    season_buttons = [
        [InlineKeyboardButton("S1", callback_data=f"setseason_1#{search}"),
         InlineKeyboardButton("S2", callback_data=f"setseason_2#{search}"),
         InlineKeyboardButton("S3", callback_data=f"setseason_3#{search}")],
        [InlineKeyboardButton("S4", callback_data=f"setseason_4#{search}"),
         InlineKeyboardButton("S5", callback_data=f"setseason_5#{search}"),
         InlineKeyboardButton("S6", callback_data=f"setseason_6#{search}")],
        [InlineKeyboardButton("S7", callback_data=f"setseason_7#{search}"),
         InlineKeyboardButton("S8", callback_data=f"setseason_8#{search}"),
         InlineKeyboardButton("S9", callback_data=f"setseason_9#{search}")],
        [InlineKeyboardButton("S10", callback_data=f"setseason_10#{search}"),
         InlineKeyboardButton("🌐 All Seasons", callback_data=f"setseason_All#{search}")],
        [InlineKeyboardButton("◀️ Back", callback_data=f"back#{search}")]
    ]
    
    await query.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(season_buttons)
    )
    await query.answer("📺 Select season")


# Episode Filter Menu
@Client.on_callback_query(filters.regex(r"^episode#"))
async def episode_menu(client, query):
    """Show episode selection menu"""
    search = query.data.split("#")[1]
    
    episode_buttons = []
    # Episodes 1-12 in 4 rows
    for i in range(0, 12, 3):
        row = []
        for j in range(3):
            ep_num = i + j + 1
            if ep_num <= 12:
                row.append(InlineKeyboardButton(f"E{ep_num:02d}", callback_data=f"setepisode_{ep_num}#{search}"))
        episode_buttons.append(row)
    
    episode_buttons.append([InlineKeyboardButton("🌐 All Episodes", callback_data=f"setepisode_All#{search}")])
    episode_buttons.append([InlineKeyboardButton("◀️ Back", callback_data=f"back#{search}")])
    
    await query.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(episode_buttons)
    )
    await query.answer("📋 Select episode")


# Apply Language Filter
@Client.on_callback_query(filters.regex(r"^setlang_"))
async def set_language_filter(client, query):
    """Apply language filter"""
    data = query.data.split("#")
    language = data[0].replace("setlang_", "")
    search = data[1]
    
    logger.info(f"🎬 Filtering by language: {language}")
    
    files, total = await db.search_files(search)
    
    if language != 'All':
        filtered_files = filter_files(files, language=language)
    else:
        filtered_files = files
    
    bot_username = await get_bot_username(client)
    
    if filtered_files:
        file_text = f"📁 Found {len(filtered_files)} {language} files for `{search}`\n\n"
        
        for file in filtered_files[:10]:
            try:
                file_id = str(file.get('_id', ''))
                original_caption = file.get('caption', '')
                file_name = file.get('file_name', 'Unknown')
                display_name = original_caption if original_caption else file_name
                cleaned_name = clean_caption(display_name)
                file_size = get_size(file.get('file_size', 0))
                
                deep_link = f"https://t.me/{bot_username}?start=file_{file_id}"
                clickable_text = f'<a href="{deep_link}">📁 {file_size} ▷ {cleaned_name}</a>'
                file_text += f"{clickable_text}\n\n"
            except Exception as e:
                logger.error(f"Error: {e}")
    else:
        file_text = f"❌ No {language} files found for `{search}`"
    
    file_text += f"\n🎬 Join: @movies_magic_club3"
    
    buttons = [
        [InlineKeyboardButton("🎭 LANGUAGE", callback_data=f"lang#{search}"),
         InlineKeyboardButton("🎬 Quality", callback_data=f"qual#{search}")],
        [InlineKeyboardButton("📺 Season", callback_data=f"season#{search}"),
         InlineKeyboardButton("📋 Episode", callback_data=f"episode#{search}")],
        [InlineKeyboardButton("18+ RARE VIDEOS💦", url="https://t.me/REAL_TERABOX_PRO_bot")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    
    try:
        await query.message.edit_text(
            file_text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )
        await query.answer(f"✅ Showing {language} files", show_alert=False)
    except Exception as e:
        logger.error(f"Error: {e}")
        await query.answer("❌ Error filtering", show_alert=True)


# Apply Quality Filter
@Client.on_callback_query(filters.regex(r"^setqual_"))
async def set_quality_filter(client, query):
    """Apply quality filter"""
    data = query.data.split("#")
    quality = data[0].replace("setqual_", "")
    search = data[1]
    
    files, total = await db.search_files(search)
    
    if quality != 'All':
        filtered_files = filter_files(files, quality=quality)
    else:
        filtered_files = files
    
    bot_username = await get_bot_username(client)
    
    if filtered_files:
        file_text = f"📁 Found {len(filtered_files)} {quality} files for `{search}`\n\n"
        
        for file in filtered_files[:10]:
            try:
                file_id = str(file.get('_id', ''))
                original_caption = file.get('caption', '')
                file_name = file.get('file_name', 'Unknown')
                display_name = original_caption if original_caption else file_name
                cleaned_name = clean_caption(display_name)
                file_size = get_size(file.get('file_size', 0))
                
                deep_link = f"https://t.me/{bot_username}?start=file_{file_id}"
                clickable_text = f'<a href="{deep_link}">📁 {file_size} ▷ {cleaned_name}</a>'
                file_text += f"{clickable_text}\n\n"
            except Exception as e:
                logger.error(f"Error: {e}")
    else:
        file_text = f"❌ No {quality} files found for `{search}`"
    
    file_text += f"\n🎬 Join: @movies_magic_club3"
    
    buttons = [
        [InlineKeyboardButton("🎭 LANGUAGE", callback_data=f"lang#{search}"),
         InlineKeyboardButton("🎬 Quality", callback_data=f"qual#{search}")],
        [InlineKeyboardButton("📺 Season", callback_data=f"season#{search}"),
         InlineKeyboardButton("📋 Episode", callback_data=f"episode#{search}")],
        [InlineKeyboardButton("18+ RARE VIDEOS💦", url="https://t.me/REAL_TERABOX_PRO_bot")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    
    try:
        await query.message.edit_text(
            file_text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )
        await query.answer(f"✅ Showing {quality} files", show_alert=False)
    except Exception as e:
        await query.answer("❌ Error filtering", show_alert=True)


# Apply Season Filter
@Client.on_callback_query(filters.regex(r"^setseason_"))
async def set_season_filter(client, query):
    """Apply season filter"""
    data = query.data.split("#")
    season = data[0].replace("setseason_", "")
    search = data[1]
    
    files, total = await db.search_files(search)
    
    if season != 'All':
        filtered_files = filter_files(files, season=season)
    else:
        filtered_files = files
    
    bot_username = await get_bot_username(client)
    
    if filtered_files:
        season_text = f"S{season}" if season != 'All' else 'All Seasons'
        file_text = f"📁 Found {len(filtered_files)} {season_text} files for `{search}`\n\n"
        
        for file in filtered_files[:10]:
            try:
                file_id = str(file.get('_id', ''))
                original_caption = file.get('caption', '')
                file_name = file.get('file_name', 'Unknown')
                display_name = original_caption if original_caption else file_name
                cleaned_name = clean_caption(display_name)
                file_size = get_size(file.get('file_size', 0))
                
                deep_link = f"https://t.me/{bot_username}?start=file_{file_id}"
                clickable_text = f'<a href="{deep_link}">📁 {file_size} ▷ {cleaned_name}</a>'
                file_text += f"{clickable_text}\n\n"
            except Exception as e:
                logger.error(f"Error: {e}")
    else:
        file_text = f"❌ No Season {season} files found for `{search}`"
    
    file_text += f"\n🎬 Join: @movies_magic_club3"
    
    buttons = [
        [InlineKeyboardButton("🎭 LANGUAGE", callback_data=f"lang#{search}"),
         InlineKeyboardButton("🎬 Quality", callback_data=f"qual#{search}")],
        [InlineKeyboardButton("📺 Season", callback_data=f"season#{search}"),
         InlineKeyboardButton("📋 Episode", callback_data=f"episode#{search}")],
        [InlineKeyboardButton("18+ RARE VIDEOS💦", url="https://t.me/REAL_TERABOX_PRO_bot")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    
    try:
        await query.message.edit_text(
            file_text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )
        await query.answer(f"✅ Showing Season {season}", show_alert=False)
    except Exception as e:
        await query.answer("❌ Error filtering", show_alert=True)


# Apply Episode Filter
@Client.on_callback_query(filters.regex(r"^setepisode_"))
async def set_episode_filter(client, query):
    """Apply episode filter"""
    data = query.data.split("#")
    episode = data[0].replace("setepisode_", "")
    search = data[1]
    
    files, total = await db.search_files(search)
    
    if episode != 'All':
        filtered_files = filter_files(files, episode=episode)
    else:
        filtered_files = files
    
    bot_username = await get_bot_username(client)
    
    if filtered_files:
        episode_text = f"E{episode}" if episode != 'All' else 'All Episodes'
        file_text = f"📁 Found {len(filtered_files)} {episode_text} files for `{search}`\n\n"
        
        for file in filtered_files[:10]:
            try:
                file_id = str(file.get('_id', ''))
                original_caption = file.get('caption', '')
                file_name = file.get('file_name', 'Unknown')
                display_name = original_caption if original_caption else file_name
                cleaned_name = clean_caption(display_name)
                file_size = get_size(file.get('file_size', 0))
                
                deep_link = f"https://t.me/{bot_username}?start=file_{file_id}"
                clickable_text = f'<a href="{deep_link}">📁 {file_size} ▷ {cleaned_name}</a>'
                file_text += f"{clickable_text}\n\n"
            except Exception as e:
                logger.error(f"Error: {e}")
    else:
        file_text = f"❌ No Episode {episode} files found for `{search}`"
    
    file_text += f"\n🎬 Join: @movies_magic_club3"
    
    buttons = [
        [InlineKeyboardButton("🎭 LANGUAGE", callback_data=f"lang#{search}"),
         InlineKeyboardButton("🎬 Quality", callback_data=f"qual#{search}")],
        [InlineKeyboardButton("📺 Season", callback_data=f"season#{search}"),
         InlineKeyboardButton("📋 Episode", callback_data=f"episode#{search}")],
        [InlineKeyboardButton("18+ RARE VIDEOS💦", url="https://t.me/REAL_TERABOX_PRO_bot")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    
    try:
        await query.message.edit_text(
            file_text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )
        await query.answer(f"✅ Showing Episode {episode}", show_alert=False)
    except Exception as e:
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
            original_caption = file.get('caption', '')
            file_name = file.get('file_name', 'Unknown')
            display_name = original_caption if original_caption else file_name
            cleaned_name = clean_caption(display_name)
            file_size = get_size(file.get('file_size', 0))
            
            deep_link = f"https://t.me/{bot_username}?start=file_{file_id}"
            clickable_text = f'<a href="{deep_link}">📁 {file_size} ▷ {cleaned_name}</a>'
            file_text += f"{clickable_text}\n\n"
        except Exception as e:
            logger.error(f"Error: {e}")
    
    file_text += f"🎬 Join: @movies_magic_club3"
    
    buttons = [
        [InlineKeyboardButton("🎭 LANGUAGE", callback_data=f"lang#{search}"),
         InlineKeyboardButton("🎬 Quality", callback_data=f"qual#{search}")],
        [InlineKeyboardButton("📺 Season", callback_data=f"season#{search}"),
         InlineKeyboardButton("📋 Episode", callback_data=f"episode#{search}")],
        [InlineKeyboardButton("18+ RARE VIDEOS💦", url="https://t.me/REAL_TERABOX_PRO_bot")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    
    await query.message.edit_text(
        file_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True
    )
    await query.answer("🔙 Back to all results")


logger.info("✅ FILTER CALLBACKS WITH SEASON & EPISODE LOADED")
                    
