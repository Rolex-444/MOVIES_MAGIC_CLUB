from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import aiohttp
import logging
from urllib.parse import quote

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
        
