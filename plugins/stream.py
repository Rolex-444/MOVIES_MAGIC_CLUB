from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.database import Database
from bson import ObjectId
from urllib.parse import quote
import aiohttp
import logging

logger = logging.getLogger(__name__)

# Initialize database
db = Database()

# Stream URLs
STREAM_URL = "https://elegant-pithivier-bc90f4.netlify.app"
TECHVJ_API = "https://techlinkapi.vercel.app"


async def get_fast_link(terabox_url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{TECHVJ_API}/getLink?link={quote(terabox_url)}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('directLink', terabox_url)
        return terabox_url
    except:
        return terabox_url


# === CALLBACK HANDLERS ONLY ===

@Client.on_callback_query(filters.regex(r"^stream_file:"))
async def handle_stream_file(client, query: CallbackQuery):
    """Handle file streaming from callback"""
    try:
        file_id = query.data.split(":", 1)[1]
        logger.info(f"Stream request for file: {file_id}")
        
        file_data = await db.get_file(ObjectId(file_id) if len(file_id) == 24 else file_id)
        if not file_data:
            await query.answer("❌ File not found!", show_alert=True)
            return
        
        name = file_data.get('file_name', 'Unknown')
        size = file_data.get('file_size', 0)
        link = file_data.get('file_link', '')
        caption = file_data.get('caption', '')
        
        size_str = f"{size/(1024**3):.2f} GB" if size > 1073741824 else f"{size/(1024**2):.2f} MB"
        
        msg = f"**File Name:** {name}\n\n**Size:** {size_str}\n\n{caption}\n\n{link}\n\n**Join:** @movies_magic_club3\n**Owner:** @Siva9789"
        
        buttons = [
            [InlineKeyboardButton("⚡ Fast Download", callback_data=f"dl:{link}")],
            [InlineKeyboardButton("🎬 Watch Online", callback_data=f"st:{link}:{name}")],
            [InlineKeyboardButton("🔞 18+ Videos", url="https://t.me/REAL_TERABOX_PRO_bot")]
        ]
        
        await query.answer("Loading file...")
        await query.message.reply(msg, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.MARKDOWN)
    
    except Exception as e:
        logger.error(f"Error: {e}")
        await query.answer("❌ Error loading file!", show_alert=True)


@Client.on_callback_query(filters.regex(r"^st:"))
async def stream_btn(client, query: CallbackQuery):
    try:
        _, url, name = query.data.split(":", 2)
        stream = f"{STREAM_URL}/?url={url}&name={quote(name)}"
        await query.answer("Opening player...")
        await query.message.reply("🎬 **Watch Online**\n\nClick below:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📺 Open Player", url=stream)]]))
    except:
        await query.answer("❌ Error!", show_alert=True)


@Client.on_callback_query(filters.regex(r"^dl:"))
async def download_btn(client, query: CallbackQuery):
    try:
        url = query.data.split(":", 1)[1]
        await query.answer("⚡ Generating link...")
        fast_link = await get_fast_link(url)
        await query.message.reply("⚡ **Fast Download**\n\nClick below:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⚡ Download", url=fast_link)]]))
    except:
        await query.answer("❌ Error!", show_alert=True)
        
