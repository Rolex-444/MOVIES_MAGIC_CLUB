from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.database import Database
from database.verify import VerifyDB
from bson import ObjectId
from info import ADMINS, SHORTLINK_URL, SHORTLINK_API, VERIFY_TUTORIAL, CUSTOM_FILE_CAPTION
from utils.shortlink_api import get_shortlink, generate_verify_token
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
    
    # Add user to database
    await db.add_user(user_id)
    
    # Check if it's a deep link
    if len(message.command) > 1:
        data = message.command[1]
        
        # File deep link
        if data.startswith("file_"):
            file_id = data.split("_", 1)[1]
            await send_file_by_deeplink(client, message, file_id)
            return
        
        # Verification token link
        elif data.startswith("verify_"):
            # Handle verification
            return
    
    # Regular /start command
    await message.reply("Welcome to the bot!")


async def send_file_by_deeplink(client, message, file_id):
    """Send file when accessed via deep link - WITH EXTENSIVE DEBUGGING"""
    user_id = message.from_user.id
    
    logger.info(f"")
    logger.info(f"{'='*70}")
    logger.info(f"📥 DEEP LINK FILE REQUEST")
    logger.info(f"{'='*70}")
    logger.info(f"👤 User ID: {user_id}")
    logger.info(f"📄 File ID: {file_id}")
    logger.info(f"🔑 ADMINS list: {ADMINS}")
    logger.info(f"❓ Is user admin? {user_id in ADMINS}")
    logger.info(f"{'='*70}")
    
    # Check if user is admin (admins bypass everything)
    if user_id not in ADMINS:
        logger.info(f"✅ User {user_id} is NOT admin - checking verification...")
        
        # Check if user can access file (verified or under free limit)
        can_access = await verify_db.can_access_file(user_id)
        
        logger.info(f"🔍 can_access_file returned: {can_access}")
        
        if not can_access:
            logger.info(f"🚫 Access DENIED - showing verification link")
            
            # User needs to verify
            token = generate_verify_token()
            await verify_db.set_verify_token(user_id, token, 600)
            
            me = await client.get_me()
            verify_url = f"https://t.me/{me.username}?start=verify_{token}"
            short_url = get_shortlink(verify_url, SHORTLINK_URL, SHORTLINK_API)
            
            buttons = [
                [InlineKeyboardButton("🔐 Verify Now", url=short_url)],
                [InlineKeyboardButton("📚 How to Verify?", url=VERIFY_TUTORIAL)],
                [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")]
            ]
            
            await message.reply(
                Config.VERIFY_TXT,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True
            )
            logger.info(f"✅ Verification message sent to user {user_id}")
            logger.info(f"{'='*70}")
            return
        
        logger.info(f"✅ Access GRANTED - preparing to send file")
        
        # Increment file attempts for non-verified users
        is_verified = await verify_db.is_verified(user_id)
        logger.info(f"🔍 is_verified returned: {is_verified}")
        
        if not is_verified:
            logger.info(f"📈 Incrementing file attempts for non-verified user")
            await verify_db.increment_file_attempts(user_id)
        else:
            logger.info(f"✅ User is verified - NOT incrementing attempts")
    else:
        logger.info(f"👑 User {user_id} IS ADMIN - bypassing all checks")
    
    logger.info(f"📤 Fetching file from database...")
    
    # Get file data from database
    try:
        if len(file_id) == 24:
            mongo_id = ObjectId(file_id)
        else:
            mongo_id = file_id
        
        file_data = await db.get_file(mongo_id)
        
    except Exception as e:
        logger.error(f"❌ Error getting file {file_id}: {e}")
        file_data = None
    
    if not file_data:
        logger.error(f"❌ File not found: {file_id}")
        await message.reply("❌ <b>File not found!</b>", parse_mode=enums.ParseMode.HTML)
        logger.info(f"{'='*70}")
        return
    
    # Build caption
    try:
        caption = CUSTOM_FILE_CAPTION if CUSTOM_FILE_CAPTION else Config.FILE_CAPTION
        caption = caption.format(
            file_name=file_data.get('file_name', 'Unknown'),
            file_size=get_size(file_data.get('file_size', 0)),
            caption=file_data.get('caption', '')
        )
    except:
        caption = f"<b>{file_data.get('file_name', 'File')}</b>\n\nJoin: @movies_magic_club3"
    
    # Build buttons
    file_buttons = [
        [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")],
        [InlineKeyboardButton("🎬 Join Channel", url="https://t.me/movies_magic_club3")]
    ]
    
    # Send file
    try:
        telegram_file_id = file_data.get('file_id')
        file_type = file_data.get('file_type', 'document')
        
        logger.info(f"📤 Sending file: {file_data.get('file_name')}, type: {file_type}")
        
        if file_type == 'video':
            await message.reply_video(
                telegram_file_id,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(file_buttons),
                parse_mode=enums.ParseMode.HTML
            )
        elif file_type == 'audio':
            await message.reply_audio(
                telegram_file_id,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(file_buttons),
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await message.reply_document(
                telegram_file_id,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(file_buttons),
                parse_mode=enums.ParseMode.HTML
            )
        
        logger.info(f"✅ File sent successfully to user {user_id}")
        logger.info(f"{'='*70}")
        
    except Exception as e:
        logger.error(f"❌ Error sending file: {e}")
        await message.reply("❌ Error sending file!")
        logger.info(f"{'='*70}")


@Client.on_message(filters.text & filters.private & ~filters.command(["start", "help", "about"]))
async def search_files(client, message):
    """Handle movie search"""
    search = message.text
    user_id = message.from_user.id
    
    logger.info(f"🔍 Search request from {user_id}: {search}")
    
    # Search in database
    files, total = await db.search_files(search)
    
    if not files:
        await message.reply(f"❌ No files found for: {search}")
        return
    
    # Get bot username
    global bot_username
    if not bot_username:
        me = await client.get_me()
        bot_username = me.username
    
    # Build file list with deep links
    file_text = f"📁 Found {total} files for: {search}\n\n"
    
    for idx, file in enumerate(files[:10], 1):
        try:
            file_id = str(file.get('_id', ''))
            file_name = file.get('file_name', 'Unknown')
            file_size = get_size(file.get('file_size', 0))
            
            # Create deep link
            deep_link = f"https://t.me/{bot_username}?start=file_{file_id}"
            
            # Format as clickable HTML link
            clickable_text = f'<a href="{deep_link}">📁 {file_size} ▷ {file_name}</a>'
            file_text += f"{clickable_text}\n\n"
            
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            continue
    
    # Add filter buttons
    buttons = [
        [
            InlineKeyboardButton("LANGUAGES", callback_data=f"lang#{search}"),
            InlineKeyboardButton("Qualitys", callback_data=f"qual#{search}"),
            InlineKeyboardButton("Season", callback_data=f"seas#{search}")
        ],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    
    await message.reply(
        file_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True
    )


@Client.on_callback_query(filters.regex("^close$"))
async def close_callback(client, query):
    """Handle close button"""
    await query.message.delete()
        
