from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.database import Database
from info import BIN_CHANNEL, URL, ADMINS, YOUR_CHANNEL, YOUR_CHANNEL_LINK, RARE_VIDEOS_LINK
from bson import ObjectId
import logging
import base64
import asyncio

logger = logging.getLogger(__name__)
db = Database()

@Client.on_callback_query(filters.regex(r"^tg_"))
async def telegram_download(client, query):
    """Send file via normal Telegram (slow but free)"""
    file_id = query.data.replace("tg_", "")
    user_id = query.from_user.id
    
    logger.info(f"📱 Telegram file request from user {user_id}")
    
    try:
        mongo_id = ObjectId(file_id)
        file_data = await db.get_file(mongo_id)
    except:
        file_data = None
    
    if not file_data:
        await query.answer("❌ File not found!", show_alert=True)
        return
    
    telegram_file_id = file_data.get('file_id')
    file_type = file_data.get('file_type', 'document')
    caption = file_data.get('caption', file_data.get('file_name', ''))
    
    try:
        if file_type == 'video':
            await query.message.reply_video(telegram_file_id, caption=caption)
        elif file_type == 'audio':
            await query.message.reply_audio(telegram_file_id, caption=caption)
        else:
            await query.message.reply_document(telegram_file_id, caption=caption)
        
        await query.answer("📱 Sending file via Telegram...", show_alert=False)
        logger.info(f"✅ Sent Telegram file to {user_id}")
    except Exception as e:
        logger.error(f"Error sending file: {e}")
        await query.answer("❌ Error sending file!", show_alert=True)

@Client.on_callback_query(filters.regex(r"^fast_"))
async def fast_download(client, query):
    """Generate fast download link via browser"""
    file_id = query.data.replace("fast_", "")
    user_id = query.from_user.id
    
    logger.info(f"⚡ Fast download request from user {user_id}")
    
    try:
        mongo_id = ObjectId(file_id)
        file_data = await db.get_file(mongo_id)
    except:
        file_data = None
    
    if not file_data:
        await query.answer("❌ File not found!", show_alert=True)
        return
    
    try:
        telegram_file_id = file_data.get('file_id')
        file_name = file_data.get('file_name', 'file')
        
        # Forward file to BIN_CHANNEL
        forwarded = await client.forward_messages(
            BIN_CHANNEL,
            query.message.chat.id,
            query.message.id
        )
        
        # Generate hash
        file_hash = base64.urlsafe_b64encode(str(forwarded.id).encode()).decode()
        
        # Save to database
        await db.save_stream_link(file_hash, forwarded.id, BIN_CHANNEL)
        
        # Generate download link
        download_link = f"{URL}/download/{file_hash}"
        
        buttons = [
            [InlineKeyboardButton("📥 Download Now", url=download_link)],
            [InlineKeyboardButton("🎬 Join Channel", url=YOUR_CHANNEL_LINK)]
        ]
        
        await query.message.reply(
            f"⚡ **Fast Download Ready!**\n\n"
            f"📁 File: {file_name}\n"
            f"📥 Click button below to download at full speed!\n\n"
            f"💡 This link is valid for 24 hours",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        
        await query.answer("✅ Download link generated!", show_alert=False)
        logger.info(f"✅ Fast download link created for {user_id}")
        
    except Exception as e:
        logger.error(f"Error creating fast download: {e}")
        await query.answer(f"❌ Error: {str(e)}", show_alert=True)

@Client.on_callback_query(filters.regex(r"^watch_"))
async def watch_online(client, query):
    """Generate watch online link (streaming)"""
    file_id = query.data.replace("watch_", "")
    user_id = query.from_user.id
    
    logger.info(f"🎬 Watch online request from user {user_id}")
    
    try:
        mongo_id = ObjectId(file_id)
        file_data = await db.get_file(mongo_id)
    except:
        file_data = None
    
    if not file_data:
        await query.answer("❌ File not found!", show_alert=True)
        return
    
    try:
        telegram_file_id = file_data.get('file_id')
        file_name = file_data.get('file_name', 'video')
        
        # Forward file to BIN_CHANNEL
        forwarded = await client.forward_messages(
            BIN_CHANNEL,
            query.message.chat.id,
            query.message.id
        )
        
        # Generate hash
        file_hash = base64.urlsafe_b64encode(str(forwarded.id).encode()).decode()
        
        # Save to database
        await db.save_stream_link(file_hash, forwarded.id, BIN_CHANNEL)
        
        # Generate watch link
        watch_link = f"{URL}/watch/{file_hash}"
        
        buttons = [
            [InlineKeyboardButton("▶️ Watch Now", url=watch_link)],
            [InlineKeyboardButton("🎬 Join Channel", url=YOUR_CHANNEL_LINK)]
        ]
        
        await query.message.reply(
            f"🎬 **Watch Online**\n\n"
            f"📺 File: {file_name}\n"
            f"▶️ Click button below to stream directly!\n\n"
            f"💡 Stream link valid for 24 hours\n"
            f"No downloading needed!",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        
        await query.answer("✅ Watch link generated!", show_alert=False)
        logger.info(f"✅ Watch online link created for {user_id}")
        
    except Exception as e:
        logger.error(f"Error creating watch link: {e}")
        await query.answer(f"❌ Error: {str(e)}", show_alert=True)
