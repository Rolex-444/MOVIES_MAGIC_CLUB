from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import STREAM_MODE, PORT
import base64

@Client.on_message(filters.command("stream") & filters.private)
async def stream_command(client, message):
    """Generate stream link"""
    
    if not STREAM_MODE:
        await message.reply(
            "⚠️ Stream mode is currently disabled!\n\n"
            "Contact @Siva9789 to enable this feature."
        )
        return
    
    if not message.reply_to_message:
        await message.reply("Reply to a file to generate stream link!")
        return
    
    if not message.reply_to_message.media:
        await message.reply("Reply to a media file!")
        return
    
    media = message.reply_to_message.document or message.reply_to_message.video
    if not media:
        await message.reply("Invalid media type!")
        return
    
    file_id = media.file_id
    
    # Encode file_id
    encoded = base64.b64encode(file_id.encode()).decode()
    stream_url = f"http://yourserver.com:{PORT}/watch/{encoded}"
    
    buttons = [
        [InlineKeyboardButton("🎬 Watch Online", url=stream_url)],
        [InlineKeyboardButton("📥 Download", url=f"http://yourserver.com:{PORT}/download/{encoded}")]
    ]
    
    await message.reply(
        f"<b>🎬 Stream Link Generated!</b>\n\n"
        f"<b>Link:</b> <code>{stream_url}</code>\n\n"
        f"Click the button to watch online!",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
