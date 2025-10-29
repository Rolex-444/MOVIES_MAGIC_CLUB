from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.database import Database
from database.verify import VerifyDB
from bson import ObjectId
from info import ADMINS, VERIFY_TUTORIAL, CUSTOM_FILE_CAPTION, FREE_FILE_LIMIT
from utils.verification import generate_verify_token, create_universal_shortlink
from config import Config
from utils.file_properties import get_size
import logging

logger = logging.getLogger(__name__)

db = Database()
verify_db = VerifyDB()

# Get bot username (set on startup)
bot_username = None


@Client.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    """Handle /start command and deep links"""
    global bot_username
    if not bot_username:
        me = await client.get_me()
        bot_username = me.username
    
    user_id = message.from_user.id
    
    logger.info(f"⭐ /start from user {user_id}")
    
    # Add user to database
    await db.add_user(user_id)
    
    # Check if it's a deep link
    if len(message.command) > 1:
        data = message.command[1]
        
        # Handle verification token
        if data.startswith("verify_"):
            token = data
            
            logger.info(f"🔍 Verification attempt by user {user_id}")
            
            token_valid = await verify_db.verify_token(user_id, token)
            
            if token_valid:
                await verify_db.update_verification(user_id)
                
                await message.reply(
                    "✅ **Verification Successful!**\n\n"
                    "You can now access unlimited files for 6 hours!\n"
                    "Search for movies in the group or send me a movie name.",
                    quote=True
                )
                logger.info(f"✅ User {user_id} successfully verified!")
            else:
                await message.reply(
                    "❌ **Verification Failed!**\n\n"
                    "Token is invalid or expired. Please try again.",
                    quote=True
                )
                logger.warning(f"❌ User {user_id} verification failed")
            return
        
        # File deep link
        elif data.startswith("file_"):
            file_id = data.split("_", 1)[1]
            await send_file_by_deeplink(client, message, file_id)
            return
    
    # Regular /start command
    await message.reply(
        "👋 Welcome!\n\n"
        "🎬 Search for movies in the group\n"
        "📁 Or send me a movie name here\n\n"
        "Join: @movies_magic_club3"
    )


async def send_file_by_deeplink(client, message, file_id):
    """Send file when accessed via deep link - WITH VERIFICATION"""
    user_id = message.from_user.id
    
    logger.info(f"📥 File request from user {user_id} for file {file_id}")
    
    # Check if user is admin (admins bypass everything)
    if user_id not in ADMINS:
        is_verified = await verify_db.is_verified(user_id)
        
        if not is_verified:
            user_data = await verify_db.get_user(user_id)
            files_sent = user_data.get('files_sent', 0) if user_data else 0
            
            if files_sent >= FREE_FILE_LIMIT:
                logger.info(f"🚫 Access DENIED - showing verification link")
                
                token = generate_verify_token()
                await verify_db.set_verify_token(user_id, f"verify_{token}", 600)
                
                me = await client.get_me()
                telegram_link = f"https://t.me/{me.username}?start=verify_{token}"
                short_url = create_universal_shortlink(telegram_link)
                
                buttons = [
                    [InlineKeyboardButton("🔐 Verify Now", url=short_url)],
                    [InlineKeyboardButton("📚 How to Verify?", url=VERIFY_TUTORIAL)]
                ]
                
                verify_msg = f"""
🔐 **Verification Required**

Hello {message.from_user.mention}!

You've used your **{files_sent}/{FREE_FILE_LIMIT} free files**.
To continue accessing more files, please verify your account.

⏰ **Verification valid for:** 6 hours
💡 **After verification:** Unlimited file access!

Click the button below to verify:
"""
                
                await message.reply(
                    verify_msg,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    parse_mode=enums.ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
                return
        
        if not is_verified:
            await verify_db.increment_files_sent(user_id)
    
    # Get file data
    try:
        if len(file_id) == 24:
            mongo_id = ObjectId(file_id)
        else:
            mongo_id = file_id
        file_data = await db.get_file(mongo_id)
    except Exception as e:
        logger.error(f"❌ Error getting file: {e}")
        file_data = None
    
    if not file_data:
        await message.reply("❌ File not found!")
        return
    
    # Build caption with better formatting
    file_name = file_data.get('file_name', 'Unknown File')
    file_size = get_size(file_data.get('file_size', 0))
    
    caption = f"""
📁 **File Name:** `{file_name}`
📦 **Size:** {file_size}

🎬 **Join:** @movies_magic_club3
"""
    
    # Build buttons
    file_buttons = [
        [InlineKeyboardButton("🎬 Join Channel", url="https://t.me/movies_magic_club3")]
    ]
    
    # Send file
    try:
        telegram_file_id = file_data.get('file_id')
        file_type = file_data.get('file_type', 'document')
        
        logger.info(f"📤 Sending: {file_name}")
        
        if file_type == 'video':
            await message.reply_video(
                telegram_file_id, 
                caption=caption, 
                reply_markup=InlineKeyboardMarkup(file_buttons), 
                parse_mode=enums.ParseMode.MARKDOWN
            )
        elif file_type == 'audio':
            await message.reply_audio(
                telegram_file_id, 
                caption=caption, 
                reply_markup=InlineKeyboardMarkup(file_buttons), 
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await message.reply_document(
                telegram_file_id, 
                caption=caption, 
                reply_markup=InlineKeyboardMarkup(file_buttons), 
                parse_mode=enums.ParseMode.MARKDOWN
            )
        
        logger.info(f"✅ File sent successfully to user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error sending file: {e}")
        await message.reply("❌ Error sending file!")


# ✅ CRITICAL FIX: Group search with higher priority
@Client.on_message(filters.text & filters.group, group=1)
async def group_search_handler(client, message):
    """Handle movie search in GROUPS"""
    search = message.text.strip()
    
    # Ignore short searches or commands
    if len(search) < 3 or search.startswith("/"):
        return
    
    logger.info(f"🔍 GROUP SEARCH from {message.chat.id}: '{search}'")
    
    try:
        files, total = await db.search_files(search)
        
        if not files or total == 0:
            logger.info(f"❌ No files found for: {search}")
            return
        
        logger.info(f"✅ Found {total} files")
        
        global bot_username
        if not bot_username:
            me = await client.get_me()
            bot_username = me.username
        
        file_text = f"📁 Found {total} files for `{search}`\n\n"
        
        for file in files[:10]:
            try:
                file_id = str(file.get('_id', ''))
                file_name = file.get('file_name', 'Unknown')
                file_size = get_size(file.get('file_size', 0))
                
                deep_link = f"https://t.me/{bot_username}?start=file_{file_id}"
                clickable_text = f'<a href="{deep_link}">📁 {file_size} ▷ {file_name}</a>'
                file_text += f"{clickable_text}\n\n"
            except Exception as e:
                logger.error(f"Error formatting file: {e}")
                continue
        
        file_text += f"🎬 Join: @movies_magic_club3"
        
        buttons = [
            [InlineKeyboardButton("🎭 LANGUAGE", callback_data=f"lang#{search}"),
             InlineKeyboardButton("🎬 Quality", callback_data=f"qual#{search}")],
            [InlineKeyboardButton("❌ Close", callback_data="close")]
        ]
        
        await message.reply(
            file_text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )
        
        logger.info(f"✅ Search results sent to group {message.chat.id}")
        
    except Exception as e:
        logger.error(f"❌ Error in group_search: {e}", exc_info=True)


@Client.on_message(filters.text & filters.private & ~filters.command(["start", "help"]))
async def private_search(client, message):
    """Handle movie search in PRIVATE chat"""
    search = message.text.strip()
    
    logger.info(f"🔍 PRIVATE SEARCH: '{search}'")
    
    try:
        files, total = await db.search_files(search)
        
        if not files:
            await message.reply(f"❌ No files found for: {search}")
            return
        
        global bot_username
        if not bot_username:
            me = await client.get_me()
            bot_username = me.username
        
        file_text = f"📁 Found {total} files for `{search}`\n\n"
        
        for file in files[:10]:
            try:
                file_id = str(file.get('_id', ''))
                file_name = file.get('file_name', 'Unknown')
                file_size = get_size(file.get('file_size', 0))
                
                deep_link = f"https://t.me/{bot_username}?start=file_{file_id}"
                clickable_text = f'<a href="{deep_link}">📁 {file_size} ▷ {file_name}</a>'
                file_text += f"{clickable_text}\n\n"
            except Exception as e:
                logger.error(f"Error: {e}")
        
        file_text += f"🎬 Join: @movies_magic_club3"
        
        buttons = [
            [InlineKeyboardButton("🎭 LANGUAGE", callback_data=f"lang#{search}"),
             InlineKeyboardButton("🎬 Quality", callback_data=f"qual#{search}")],
            [InlineKeyboardButton("❌ Close", callback_data="close")]
        ]
        
        await message.reply(
            file_text, 
            reply_markup=InlineKeyboardMarkup(buttons), 
            parse_mode=enums.ParseMode.HTML, 
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger.error(f"❌ Error in private_search: {e}", exc_info=True)


@Client.on_callback_query(filters.regex("^close$"))
async def close_callback(client, query):
    """Handle close button"""
    await query.message.delete()
    await query.answer()


# Log that this plugin loaded
logger.info("✅ FILTERS PLUGIN LOADED")
    
