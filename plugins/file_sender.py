from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.database import Database
from bson import ObjectId
from urllib.parse import quote
import aiohttp
import logging

logger = logging.getLogger(__name__)

db = Database()

# Streaming URLs
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


@Client.on_message(filters.command("start") & filters.private & filters.regex(r"^/start file_"))
async def handle_file_request(client, message):
    """Handle file deep links like /start file_xxxxx"""
    file_id = message.text.split("_", 1)[1] if "_" in message.text else None
    
    if not file_id:
        return
    
    user_id = message.from_user.id
    logger.info(f"File request from {user_id}: {file_id}")
    
    try:
        file_data = await db.get_file(ObjectId(file_id) if len(file_id) == 24 else file_id)
        if not file_data:
            await message.reply("❌ File not found!")
            return
        
        name = file_data.get('file_name', 'Unknown')
        size = file_data.get('file_size', 0)
        link = file_data.get('file_link', '')
        caption = file_data.get('caption', '')
        telegram_file_id = file_data.get('file_id')  # Get Telegram file ID
        file_type = file_data.get('file_type', 'document')
        
        size_str = f"{size/(1024**3):.2f} GB" if size > 1073741824 else f"{size/(1024**2):.2f} MB"
        
        # Build caption
        msg = f"**{name}**\n\n📊 **Size:** {size_str}\n\n{caption}\n\n🔗 {link}\n\n**Join:** @movies_magic_club3\n**Owner:** @Siva9789"
        
        # === STREAMING BUTTONS ===
        buttons = [
            [InlineKeyboardButton("⚡ Fast Download", callback_data=f"dl:{link}")],
            [InlineKeyboardButton("🎬 Watch Online", callback_data=f"st:{link}:{name}")],
            [InlineKeyboardButton("🔞 18+ Videos", url="https://t.me/REAL_TERABOX_PRO_bot")],
            [InlineKeyboardButton("🎬 Join Channel", url="https://t.me/movies_magic_club3")]
        ]
        
        # Send actual Telegram file if file_id exists
        if telegram_file_id:
            try:
                if file_type == 'video':
                    await message.reply_video(
                        telegram_file_id,
                        caption=msg,
                        reply_markup=InlineKeyboardMarkup(buttons),
                        parse_mode=enums.ParseMode.MARKDOWN
                    )
                else:
                    await message.reply_document(
                        telegram_file_id,
                        caption=msg,
                        reply_markup=InlineKeyboardMarkup(buttons),
                        parse_mode=enums.ParseMode.MARKDOWN
                    )
                return
            except Exception as e:
                logger.error(f"Failed to send file: {e}")
        
        # Fallback: send text message if file sending fails
        await message.reply(msg, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.MARKDOWN)
    
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.reply("❌ Error loading file!")


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
        
