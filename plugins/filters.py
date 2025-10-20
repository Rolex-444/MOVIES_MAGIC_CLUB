from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.database import Database
from database.verify import VerifyDB
from database.users import UserDB
from utils.filters_func import search_files
from utils.shortlink_api import get_shortlink
from utils.file_properties import get_size
from info import *
from config import Config
import random
import asyncio

db = Database()
verify_db = VerifyDB()
user_db = UserDB()

@Client.on_message(filters.text & filters.group)
async def auto_filter(client, message):
    """Main auto filter function"""
    
    # Ignore commands
    if message.text.startswith('/'):
        return
    
    # Get search query
    search = message.text
    
    # Search files in database
    files, offset, total = await search_files(search)
    
    if not files:
        # No files found
        if SPELL_CHECK:
            await spell_check(client, message, search)
        return
    
    # Build buttons
    btn = []
    for file in files:
        # Create unique file ID
        file_id = str(file.get('_id'))
        file_name = file.get('file_name', 'Unknown')
        
        # Create button with verification link
        if IS_VERIFY:
            verify_url = f"https://t.me/{client.username}?start=file_{file_id}"
            short_url = await get_shortlink(verify_url)
            btn.append([InlineKeyboardButton(f"📁 {file_name}", url=short_url)])
        else:
            btn.append([InlineKeyboardButton(f"📁 {file_name}", callback_data=f"file#{file_id}")])
    
    # Add pages navigation if more files
    if offset != "":
        btn.append(
            [InlineKeyboardButton("📄 Pages", callback_data="pages"),
             InlineKeyboardButton(f"1/{round(int(total)/10)}", callback_data="pages"),
             InlineKeyboardButton("Next ⏩", callback_data=f"next_{offset}")]
        )
    
    # Add 18+ Rare Videos button
    btn.append([InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")])
    
    # Add close button
    btn.append([InlineKeyboardButton("❌ Close", callback_data="close")])
    
    # Get IMDB info if enabled
    if IMDB:
        imdb_info = await get_imdb_info(search)
        caption = format_caption(imdb_info, total)
    else:
        caption = f"<b>Found {total} results for:</b> <code>{search}</code>\n\n"
    
    # Send results
    try:
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=caption,
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except Exception as e:
        await message.reply(
            caption,
            reply_markup=InlineKeyboardMarkup(btn)
        )


@Client.on_callback_query(filters.regex(r"^file#"))
async def send_file(client, query):
    """Send file after verification check"""
    
    user_id = query.from_user.id
    file_id = query.data.split("#")[1]
    
    # Check verification status
    if IS_VERIFY and user_id not in ADMINS:
        is_verified = await verify_db.is_verified(user_id)
        
        if not is_verified:
            verify_url = f"https://t.me/{client.username}?start=verify_{user_id}"
            short_url = await get_shortlink(verify_url)
            
            buttons = [
                [InlineKeyboardButton("🔐 Verify Now", url=short_url)],
                [InlineKeyboardButton("📚 How to Verify?", url=VERIFY_TUTORIAL)],
                [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")]
            ]
            
            await query.answer(
                "⚠️ You need to verify first!",
                show_alert=True
            )
            
            await query.message.reply(
                Config.VERIFY_TXT,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return
    
    # Get file from database
    file_data = await db.get_file(file_id)
    
    if not file_data:
        await query.answer("File not found!", show_alert=True)
        return
    
    # Send file
    caption = CUSTOM_FILE_CAPTION if CUSTOM_FILE_CAPTION else Config.FILE_CAPTION
    caption = caption.format(
        file_name=file_data.get('file_name', 'Unknown'),
        file_size=get_size(file_data.get('file_size', 0)),
        caption=file_data.get('caption', '')
    )
    
    # Buttons for file message with Stream, Fast Download, and 18+ button
    file_buttons = [
        [InlineKeyboardButton("🎬 Stream", callback_data=f"stream#{file_id}"),
         InlineKeyboardButton("⚡ Fast Download", callback_data=f"fast#{file_id}")],
        [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")],
        [InlineKeyboardButton("🎬 Join Channel", url="https://t.me/movies_magic_club3")]
    ]
    
    try:
        msg = await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_data.get('file_id'),
            caption=caption,
            protect_content=PROTECT_CONTENT,
            reply_markup=InlineKeyboardMarkup(file_buttons)
        )
        
        await query.answer("File sent to PM!", show_alert=False)
        
        # Auto delete if enabled
        if AUTO_DELETE:
            await asyncio.sleep(AUTO_DELETE_TIME)
            try:
                await msg.delete()
            except:
                pass
            
    except Exception as e:
        await query.answer(f"Error: {e}", show_alert=True)


async def send_file_by_id(client, message, file_id):
    """Send file by ID from start command"""
    user_id = message.from_user.id
    
    # Get file from database
    file_data = await db.get_file(file_id)
    
    if not file_data:
        await message.reply("File not found!")
        return
    
    # Send file
    caption = CUSTOM_FILE_CAPTION if CUSTOM_FILE_CAPTION else Config.FILE_CAPTION
    caption = caption.format(
        file_name=file_data.get('file_name', 'Unknown'),
        file_size=get_size(file_data.get('file_size', 0)),
        caption=file_data.get('caption', '')
    )
    
    # Buttons for file message
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
            protect_content=PROTECT_CONTENT,
            reply_markup=InlineKeyboardMarkup(file_buttons)
        )
        
        # Auto delete if enabled
        if AUTO_DELETE:
            await asyncio.sleep(AUTO_DELETE_TIME)
            try:
                await msg.delete()
            except:
                pass
            
    except Exception as e:
        await message.reply(f"Error: {e}")


@Client.on_callback_query(filters.regex(r"^stream#"))
async def stream_callback(client, query):
    """Handle stream button callback"""
    file_id = query.data.split("#")[1]
    
    if STREAM_MODE:
        # Generate stream link
        import base64
        encoded = base64.b64encode(file_id.encode()).decode()
        stream_url = f"http://yourserver.com:{PORT}/watch/{encoded}"
        
        await query.answer(
            f"Stream Link: {stream_url}",
            show_alert=True
        )
    else:
        await query.answer(
            "⚠️ Stream feature is currently disabled!\n\nContact @Siva9789 to enable.",
            show_alert=True
        )


@Client.on_callback_query(filters.regex(r"^fast#"))
async def fast_download_callback(client, query):
    """Handle fast download button"""
    file_id = query.data.split("#")[1]
    
    # Get file from database
    file_data = await db.get_file(file_id)
    
    if not file_data:
        await query.answer("File not found!", show_alert=True)
        return
    
    # Check if user is premium
    user_id = query.from_user.id
    is_premium = await user_db.is_premium(user_id)
    
    if not is_premium:
        await query.answer(
            "⚠️ Fast Download is only for Premium users!\n\n"
            "Use /premium to get premium access.",
            show_alert=True
        )
        return
    
    # Send file without verification for premium users
    caption = f"⚡ <b>Fast Download</b>\n\n{file_data.get('file_name', 'Unknown')}\n\nEnjoy Premium! 👑"
    
    try:
        await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_data.get('file_id'),
            caption=caption,
            protect_content=PROTECT_CONTENT
        )
        await query.answer("✅ File sent instantly!", show_alert=False)
    except Exception as e:
        await query.answer(f"Error: {e}", show_alert=True)


async def spell_check(client, message, search):
    """Spell check for wrong movie names"""
    # Implement spell check logic here if needed
    pass


async def get_imdb_info(title):
    """Get IMDB information"""
    try:
        from imdb import IMDb
        ia = IMDb()
        movies = ia.search_movie(title)
        
        if movies:
            movie = movies[0]
            ia.update(movie)
            return {
                'title': movie.get('title'),
                'year': movie.get('year'),
                'rating': movie.get('rating'),
                'genres': ', '.join(movie.get('genres', [])),
                'plot': movie.get('plot outline'),
                'poster': movie.get('full-size cover url')
            }
    except:
        pass
    return None


def format_caption(imdb_info, total):
    """Format caption with IMDB info"""
    if not imdb_info:
        return f"<b>Found {total} results</b>\n\n"
    
    caption = f"""
🎬 <b>{imdb_info['title']}</b> ({imdb_info.get('year', 'N/A')})

⭐ <b>Rating:</b> {imdb_info.get('rating', 'N/A')}/10
🎭 <b>Genres:</b> {imdb_info.get('genres', 'N/A')}

📝 <b>Plot:</b> {imdb_info.get('plot', 'N/A')[:200]}...

<b>Found {total} results:</b>
"""
    return caption
