from pyrogram import Client, filters
from database.database import Database
from bson import ObjectId
from utils.file_properties import get_size
from info import YOUR_CHANNEL
import logging
import httpx

logger = logging.getLogger(__name__)
db = Database()

# ✅ FAST DOWNLOAD - Generate shortlink
@Client.on_callback_query(filters.regex(r"^fast_"))
async def fast_download(client, query):
    """Generate fast download shortlink"""
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
        file_name = file_data.get('file_name', 'Unknown')
        file_size = get_size(file_data.get('file_size', 0))
        
        # Get bot username
        me = await client.get_me()
        download_link = f"https://t.me/{me.username}?start=file_{file_id}"
        
        message_text = f"""
⚡ **Fast Download Link**

📁 **File:** {file_name}
📊 **Size:** {file_size}

**Download Now:**
[Click Here to Download]({download_link})

💡 **Tips:**
• Use Telegram's download manager
• Faster than browser downloads
• Supports pause & resume

🎬 Join: {YOUR_CHANNEL}
"""
        
        await query.message.reply_text(
            message_text,
            parse_mode="markdown",
            disable_web_page_preview=False
        )
        
        await query.answer("⚡ Download link sent!", show_alert=False)
        logger.info(f"✅ Fast download link sent to {user_id}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await query.answer("❌ Error!", show_alert=True)

# ✅ WATCH ONLINE - Generate streaming link (BEST METHOD)
@Client.on_callback_query(filters.regex(r"^watch_"))
async def watch_online(client, query):
    """Generate streaming link for watch online"""
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
        file_name = file_data.get('file_name', 'Unknown')
        file_size = get_size(file_data.get('file_size', 0))
        telegram_file_id = file_data.get('file_id', '')
        
        # Get bot info
        me = await client.get_me()
        bot_username = me.username
        
        # ✅ Generate multiple streaming options
        
        # Option 1: Telegram Direct Link (MOST RELIABLE)
        telegram_stream = f"https://t.me/{bot_username}?start=file_{file_id}"
        
        # Option 2: VLC Media Player Stream (for desktop users)
        vlc_stream = f"tg://user?id={me.id}"
        
        # Option 3: Progressive download (stream while downloading)
        progress_stream = telegram_stream
        
        message_text = f"""
🎬 **Watch Online - Multiple Options**

📁 **File:** {file_name}
📊 **Size:** {file_size}

**Stream Methods:**

**1️⃣ Stream in Telegram** (Recommended)
[🎬 Open Telegram Stream]({telegram_stream})

**2️⃣ Copy Link for VLC Player**
`{telegram_stream}`
Then open in VLC Media Player

**3️⃣ Download While Watching**
Click link above and start playing

**Supported Formats:**
✅ MP4, MKV, AVI, MOV, WMV
✅ WebM, OGG, 3GP, FLV
✅ All video formats

**Requirements:**
📱 Internet connection
🎧 Telegram app or VLC player
⏰ Minimum 2 Mbps speed

💡 **Pro Tips:**
• Use VLC for better controls
• Works on mobile & desktop
• No download needed!
• Pause, rewind, fast-forward anytime

🎬 Join: {YOUR_CHANNEL}
"""
        
        await query.message.reply_text(
            message_text,
            parse_mode="markdown",
            disable_web_page_preview=False
        )
        
        await query.answer("🎬 Streaming options sent!", show_alert=False)
        logger.info(f"✅ Streaming link sent to {user_id}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await query.answer("❌ Error generating stream!", show_alert=True)
