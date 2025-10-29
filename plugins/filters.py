from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.database import Database
from database.verify import VerifyDB
from bson import ObjectId
from info import ADMINS, VERIFY_TUTORIAL, CUSTOM_FILE_CAPTION, FREE_FILE_LIMIT
from utils.verification import generate_verify_token, generate_monetized_verification_link
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
        
        # Handle file requests
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
        "I'm a movie filter bot. Send me a movie name to search!",
        quote=True
    )


async def send_file_with_verification(client, message, file_data):
    """Send file with verification check"""
    user_id = message.from_user.id
    
    # Check if user is verified
    is_verified = await verify_db.is_verified(user_id)
    user_data = await verify_db.get_user(user_id)
    
    if not is_verified:
        # Check free file limit
        files_sent = user_data.get('files_sent', 0) if user_data else 0
        
        logger.info(f"📊 User {user_id}: files_sent={files_sent}, limit={FREE_FILE_LIMIT}")
        
        if files_sent >= FREE_FILE_LIMIT:
            # Generate verification link
            token = generate_verify_token()
            await verify_db.set_verify_token(user_id, f"verify_{token}", 600)  # 10 min expiry
            
            # Get bot username
            if not bot_username:
                me = await client.get_me()
                bot_username = me.username
            
            # Create monetized shortlink
            verify_link = generate_monetized_verification_link(bot_username, token)
            
            buttons = [
                [InlineKeyboardButton("🔐 Verify Now", url=verify_link)],
                [InlineKeyboardButton("📚 How to Verify?", url=VERIFY_TUTORIAL)]
            ]
            
            await message.reply(
                Config.VERIFY_TXT.format(
                    first=message.from_user.first_name,
                    last=message.from_user.last_name or "",
                    username=f"@{message.from_user.username}" if message.from_user.username else "User",
                    mention=message.from_user.mention,
                    id=user_id
                ),
                reply_markup=InlineKeyboardMarkup(buttons),
                quote=True
            )
            logger.info(f"🔒 User {user_id} needs verification - {files_sent}/{FREE_FILE_LIMIT} files used")
            return
    
    # Send the file
    try:
        file_caption = CUSTOM_FILE_CAPTION.format(
            file_name=file_data.get('file_name', 'Unknown'),
            file_size=get_size(file_data.get('file_size', 0)),
            file_caption=file_data.get('caption', '')
        ) if CUSTOM_FILE_CAPTION else file_data.get('file_name', 'File')
        
        await client.send_cached_media(
            chat_id=message.chat.id,
            file_id=file_data['file_id'],
            caption=file_caption,
            reply_to_message_id=message.id
        )
        
        # Increment file counter for non-verified users
        if not is_verified:
            await verify_db.increment_files_sent(user_id)
            logger.info(f"📈 User {user_id} file counter incremented to {files_sent + 1}")
        
        logger.info(f"✅ File sent to user {user_id}")
        
    except Exception as e:
        logger.error(f"Error sending file: {e}")
        await message.reply("❌ Error sending file!")


@Client.on_message(filters.text & filters.private & ~filters.command(['start']))
async def search_files(client, message):
    """Search and display files"""
    user_id = message.from_user.id
    search_query = message.text
    
    # Search for files
    files = await db.search_files(search_query)
    
    if not files:
        await message.reply(
            f"❌ No results found for '{search_query}'\n\n"
            "Try different keywords!",
            quote=True
        )
        return
    
    # Display results
    buttons = []
    for file in files[:50]:  # Limit to 50 results
        file_id_str = str(file['_id'])
        file_name = file.get('file_name', 'Unknown')
        file_size = get_size(file.get('file_size', 0))
        
        button_text = f"📁 {file_name} ({file_size})"
        buttons.append([InlineKeyboardButton(
            button_text,
            callback_data=f"file_{file_id_str}"
        )])
    
    await message.reply(
        f"🔍 Found {len(files)} results for '{search_query}'\n\n"
        "Click on a file to download:",
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True
    )


@Client.on_callback_query(filters.regex("^file_"))
async def file_callback(client, query: CallbackQuery):
    """Handle file button clicks"""
    file_id_str = query.data.split("_", 1)[1]
    
    try:
        file_data = await db.get_file_by_id(file_id_str)
        if file_data:
            # Create a fake message object for send_file_with_verification
            query.message.from_user = query.from_user
            await send_file_with_verification(client, query.message, file_data)
            await query.answer("✅ Processing your request...")
        else:
            await query.answer("❌ File not found!", show_alert=True)
    except Exception as e:
        logger.error(f"Error in file callback: {e}")
        await query.answer("❌ Error fetching file!", show_alert=True)
    
