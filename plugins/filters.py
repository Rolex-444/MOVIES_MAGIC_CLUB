from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
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
    
    # Add user to database
    await db.add_user(user_id, message.from_user.first_name)
    
    # Check if it's a deep link
    if len(message.command) > 1:
        payload = message.command[1]
        
        # Handle verification token
        if payload.startswith('verify_'):
            token = payload  # Keep full token with prefix
            
            logger.info(f"🔍 Verification attempt by user {user_id} with token {token}")
            
            # Verify the token
            token_valid = await verify_db.verify_token(user_id, token)
            
            if token_valid:
                # ✅ CRITICAL: Mark user as verified
                await verify_db.update_verification(user_id)
                
                await message.reply(
                    "✅ **Verification Successful!**\n\n"
                    "You can now access files without verification for 6 hours.\n"
                    "Send me a movie name to search!",
                    quote=True
                )
                logger.info(f"✅ User {user_id} successfully verified!")
            else:
                await message.reply(
                    "❌ **Verification Failed!**\n\n"
                    "Token is invalid or expired. Please try again.",
                    quote=True
                )
                logger.warning(f"❌ User {user_id} verification failed - invalid token")
            return
        
        # Handle file requests (from inline buttons)
        elif len(payload) == 24:  # MongoDB ObjectId
            try:
                file_data = await db.get_file_by_id(payload)
                if file_data:
                    await send_file_with_verification(client, message, file_data)
                else:
                    await message.reply("❌ File not found!")
            except Exception as e:
                logger.error(f"Error fetching file: {e}")
                await message.reply("❌ Error fetching file!")
            return
    
    # Normal start message
    await message.reply(
        f"👋 Hello {message.from_user.mention}!\n\n"
        "I'm a movie filter bot. Send me a movie name to search!\n\n"
        "Example: Aranmanai",
        quote=True
    )


async def send_file_with_verification(client, message, file_data):
    """Send file with verification check"""
    user_id = message.from_user.id
    
    logger.info(f"📤 Attempting to send file to user {user_id}")
    
    # Check if user is verified
    is_verified = await verify_db.is_verified(user_id)
    user_data = await verify_db.get_user(user_id)
    
    if not is_verified:
        # Check free file limit
        files_sent = user_data.get('files_sent', 0) if user_data else 0
        
        logger.info(f"📊 User {user_id}: files_sent={files_sent}, limit={FREE_FILE_LIMIT}, verified={is_verified}")
        
        if files_sent >= FREE_FILE_LIMIT:
            # Generate verification link
            token = generate_verify_token()
            await verify_db.set_verify_token(user_id, f"verify_{token}", 600)  # 10 min expiry
            
            # Get bot username
            if not bot_username:
                me = await client.get_me()
                bot_username = me.username
            
            # Create Telegram link
            telegram_link = f"https://t.me/{bot_username}?start=verify_{token}"
            
            # Create monetized shortlink
            verify_link = create_universal_shortlink(telegram_link)
            
            buttons = [
                [InlineKeyboardButton("🔐 Verify Now", url=verify_link)],
                [InlineKeyboardButton("📚 How to Verify?", url=VERIFY_TUTORIAL)]
            ]
            
            verify_message = f"""
🔐 **Verification Required**

Hello {message.from_user.mention}!

You've used your **{files_sent}/{FREE_FILE_LIMIT} free files**.
To continue accessing more files, please verify your account.

⏰ **Verification valid for:** 6 hours
💡 **After verification:** Unlimited file access!

Click the button below to verify:
"""
            
            await message.reply(
                verify_message,
                reply_markup=InlineKeyboardMarkup(buttons),
                quote=True
            )
            logger.info(f"🔒 User {user_id} needs verification - {files_sent}/{FREE_FILE_LIMIT} files used")
            return
    
    # Send the file
    try:
        # Get file caption
        if CUSTOM_FILE_CAPTION:
            file_caption = CUSTOM_FILE_CAPTION.format(
                file_name=file_data.get('file_name', 'Unknown'),
                file_size=get_size(file_data.get('file_size', 0)),
                file_caption=file_data.get('caption', '')
            )
        else:
            file_caption = file_data.get('file_name', 'File')
        
        # Send file based on type
        file_id = file_data.get('file_id')
        file_type = file_data.get('file_type', 'document')
        
        if file_type == 'video':
            await client.send_video(
                chat_id=message.chat.id,
                video=file_id,
                caption=file_caption,
                reply_to_message_id=message.id
            )
        elif file_type == 'document':
            await client.send_document(
                chat_id=message.chat.id,
                document=file_id,
                caption=file_caption,
                reply_to_message_id=message.id
            )
        else:
            # Try send_cached_media for any type
            await client.send_cached_media(
                chat_id=message.chat.id,
                file_id=file_id,
                caption=file_caption,
                reply_to_message_id=message.id
            )
        
        # Increment file counter for non-verified users
        if not is_verified:
            await verify_db.increment_files_sent(user_id)
            files_sent = user_data.get('files_sent', 0) if user_data else 0
            logger.info(f"📈 User {user_id} file counter incremented to {files_sent + 1}")
        
        logger.info(f"✅ File sent successfully to user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error sending file to user {user_id}: {e}")
        await message.reply("❌ Error sending file! Please try again.")


# This handler must match your existing bot structure
# If your bot uses a different search method, keep your original one
