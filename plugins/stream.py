from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import db
from bson import ObjectId
from urllib.parse import quote
import aiohttp
import logging

logger = logging.getLogger(__name__)

# Your Netlify Stream Website URL
STREAM_WEBSITE_URL = "https://elegant-pithivier-bc90f4.netlify.app"

# TechVJ API for direct links
TECHVJ_API = "https://techlinkapi.vercel.app"


async def get_direct_download_link(terabox_url):
    """Get fast download link from TechVJ API"""
    try:
        async with aiohttp.ClientSession() as session:
            api_url = f"{TECHVJ_API}/getLink?link={quote(terabox_url)}"
            async with session.get(api_url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('status') == 'success':
                        return data.get('directLink', terabox_url)
        return terabox_url
    except Exception as e:
        logger.error(f"Error getting direct link: {e}")
        return terabox_url


@Client.on_message(filters.command("start") & filters.private)
async def handle_file_deep_link(client, message):
    """Handle deep link file access like /start file_xxxxx"""
    
    # Only handle if there's a parameter
    if len(message.command) <= 1:
        return
    
    data = message.command[1]
    
    # Only handle file deep links
    if not data.startswith("file_"):
        return
    
    user_id = message.from_user.id
    file_id = data.replace("file_", "")
    
    logger.info(f"Deep link file access: user {user_id}, file_id {file_id}")
    
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
    file_size = file_data.get('file_size', 0)
    caption = file_data.get('caption', '')
    file_link = file_data.get('file_link', '')  # Terabox link
    
    # Format size
    size_str = f"{file_size / (1024**3):.2f} GB" if file_size > 1073741824 else f"{file_size / (1024**2):.2f} MB"
    
    # Build caption
    msg_caption = f"**File Name:** {file_name}\n\n**Size:** {size_str}\n\n{caption}\n\n{file_link}\n\n**Join:** @movies_magic_club3\n**Owner:** @Siva9789"
    
    # === STREAMING BUTTONS ===
    buttons = [
        [InlineKeyboardButton("⚡ Fast Download", callback_data=f"download:{file_link}")],
        [InlineKeyboardButton("🎬 Watch Online", callback_data=f"stream:{file_link}:{file_name}")],
        [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")],
        [InlineKeyboardButton("🎬 Join Channel", url="https://t.me/movies_magic_club3")]
    ]
    
    # Send file details with thumbnail if available
    thumbnail = file_data.get('thumbnail')
    
    try:
        if thumbnail:
            await message.reply_photo(
                photo=thumbnail,
                caption=msg_caption,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await message.reply(
                msg_caption,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.MARKDOWN
            )
    except Exception as e:
        logger.error(f"Error sending file details: {e}")
        await message.reply(msg_caption, reply_markup=InlineKeyboardMarkup(buttons))


# === CALLBACK HANDLERS FOR BUTTONS ===

@Client.on_callback_query(filters.regex(r"^stream:"))
async def handle_stream_watch(client, query: CallbackQuery):
    """Handle Watch Online button"""
    try:
        _, encoded_url, filename = query.data.split(":", 2)
        stream_url = f"{STREAM_WEBSITE_URL}/?url={encoded_url}&name={quote(filename)}"
        
        buttons = [[InlineKeyboardButton("📺 Open Stream Player", url=stream_url)]]
        
        await query.answer("Opening streaming player...", show_alert=False)
        await query.message.reply(
            "🎬 **Watch Online**\n\nClick the button below to open the streaming player in your browser.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        logger.error(f"Error in stream handler: {e}")
        await query.answer("❌ Error opening stream!", show_alert=True)


@Client.on_callback_query(filters.regex(r"^download:"))
async def handle_fast_download(client, query: CallbackQuery):
    """Handle Fast Download button"""
    try:
        _, encoded_url = query.data.split(":", 1)
        
        await query.answer("⚡ Generating fast download link...", show_alert=False)
        download_link = await get_direct_download_link(encoded_url)
        
        buttons = [[InlineKeyboardButton("⚡ Download Now", url=download_link)]]
        
        await query.message.reply(
            "⚡ **Fast Download**\n\nClick the button below to start downloading at maximum speed.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        logger.error(f"Error in download handler: {e}")
        await query.answer("❌ Error generating download link!", show_alert=True)
    
